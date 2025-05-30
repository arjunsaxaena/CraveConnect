from typing import Dict, List, Any, Optional, TypedDict, Literal
import asyncio
from langgraph.graph import StateGraph
from app.query_refiner import refine_query
from app.embedder import generate_embedding
from app.vector_search import search_similar_dishes
from app.reranker import rerank_recommendations  # Import the new reranker
from app.config import logger
import google.generativeai as genai
from app.config import logger, GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
health_model = genai.GenerativeModel('gemini-2.0-flash', 
                                   generation_config={"temperature": 0.1})

class RecommendationState(TypedDict):
    original_query: str
    refined_query: Optional[str]
    confidence: float
    embedding: Optional[List[float]]
    recommendations: List[Dict[str, Any]]
    top_k: int
    error: Optional[str]

async def refine_query_node(state: RecommendationState) -> RecommendationState:
    """Refine the query if needed and update state."""
    try:
        # Now refine_query will loop internally until it reaches confidence threshold
        refined_query, confidence = await refine_query(state["original_query"])
        
        return {
            **state,
            "refined_query": refined_query,
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"Error in refine_query_node: {str(e)}")
        return {
            **state,
            "refined_query": state["original_query"],
            "confidence": 1.0,
            "error": f"Failed to refine query: {str(e)}"
        }

async def generate_embedding_node(state: RecommendationState) -> RecommendationState:
    """Generate embedding for the query."""
    try:
        # Use refined query if available, otherwise original query
        query_to_embed = state.get("refined_query") or state["original_query"]
        
        embedding = await generate_embedding(query_to_embed)
        
        return {
            **state,
            "embedding": embedding
        }
    except Exception as e:
        logger.error(f"Error in generate_embedding_node: {str(e)}")
        return {
            **state,
            "embedding": None,
            "error": f"Failed to generate embedding: {str(e)}"
        }

async def search_dishes_node(state: RecommendationState) -> RecommendationState:
    """Search for similar dishes using the embedding."""
    try:
        if not state.get("embedding"):
            return {
                **state,
                "recommendations": [],
                "error": "No valid embedding available for search"
            }
            
        recommendations = await search_similar_dishes(
            state["embedding"], 
            top_k=state.get("top_k", 5)
        )
        
        return {
            **state,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error in search_dishes_node: {str(e)}")
        return {
            **state,
            "recommendations": [],
            "error": f"Failed to search dishes: {str(e)}"
        }

async def rerank_results_node(state: RecommendationState) -> RecommendationState:
    """Rerank results using LLM for better semantic understanding."""
    try:
        if not state.get("recommendations"):
            return state
            
        # Use the refined query if available, otherwise original
        query_for_reranking = state.get("refined_query") or state["original_query"]
        
        # Get more results for reranking and deduplicate later
        more_results_count = state.get("top_k", 5) * 2
        
        # If we have fewer than requested results, use what we have
        if more_results_count > len(state.get("recommendations", [])):
            results_to_rerank = state.get("recommendations", [])
        else:
            # Use existing results rather than making a new query
            results_to_rerank = state.get("recommendations", [])
        
        # Rerank with semantic understanding
        reranked_results = await rerank_recommendations(
            query=query_for_reranking,
            recommendations=results_to_rerank
        )
        
        # Only take the top_k after reranking
        final_results = reranked_results[:state.get("top_k", 5)]
        
        return {
            **state,
            "recommendations": final_results
        }
    except Exception as e:
        logger.error(f"Error in rerank_results_node: {str(e)}")
        return state  # Fall back to vector search results

async def analyze_health_attributes_node(state: RecommendationState) -> RecommendationState:
    """Analyze health attributes of recommendations when health-related query is detected."""
    if not state.get("recommendations"):
        return state
        
    # Check if query is health-related
    query = state.get("original_query", "").lower() + " " + (state.get("refined_query", "").lower() or "")
    health_related_terms = ["health", "healthy", "nutritious", "diet", "calorie", "fresh", "light", "wont be too much"]
    
    is_health_query = any(term in query for term in health_related_terms)
    
    if not is_health_query:
        logger.info("Query not health-related, skipping health analysis")
        return state
        
    logger.info("Detected health-related query, performing health analysis")
    
    try:
        # Prepare items for batch analysis
        items_for_analysis = []
        for item in state.get("recommendations", []):
            items_for_analysis.append({
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description", "") or ""
            })
        
        if not items_for_analysis:
            return state
            
        # Create health analysis prompt
        prompt = """
        For each food item, evaluate its health value on a scale of 0-100 where:
        - 100 = Extremely healthy (e.g., fresh salad with lean protein)
        - 70 = Moderately healthy (e.g., grilled chicken sandwich)
        - 50 = Neutral (e.g., pasta with light sauce)
        - 30 = Somewhat unhealthy (e.g., pizza)
        - 0 = Very unhealthy (e.g., deep-fried foods with heavy sauce)
        
        Consider:
        - Ingredients (fresh vegetables vs. processed ingredients)
        - Preparation methods (grilled vs. fried)
        - Nutrient profile (high protein/fiber vs. high sugar/fat)
        
        Return only a JSON array with scores. Format:
        [
          {"id": "item_id_1", "health_score": 75},
          {"id": "item_id_2", "health_score": 30}
        ]
        
        Food items to evaluate:
        """
        
        for item in items_for_analysis:
            prompt += f"\n- ID: {item['id']}, Name: {item['name']}, Description: {item['description']}"
            
        # Get health analysis
        response = await asyncio.to_thread(
            health_model.generate_content,
            prompt
        )
        
        # Parse response 
        import json
        import re
        
        # Extract JSON using regex in case there's surrounding text
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if json_match:
            try:
                health_scores = json.loads(json_match.group(0))
                
                # Create ID to score mapping
                id_to_health_score = {item["id"]: item["health_score"] for item in health_scores if "id" in item and "health_score" in item}
                
                # Apply health scores and add reason
                for item in state.get("recommendations", []):
                    if item["id"] in id_to_health_score:
                        item["health_score"] = id_to_health_score[item["id"]]
                    else:
                        item["health_score"] = 50  # Default neutral score
                        
                # Re-sort results using combined health and relevance score
                # Health is weighted more heavily for health queries
                state["recommendations"] = sorted(
                    state["recommendations"], 
                    key=lambda x: (x.get("similarity_score", 0) * 0.3 + x.get("health_score", 50) * 0.7) / 100,
                    reverse=True
                )
                
                logger.info(f"Health analysis complete - reordered {len(state['recommendations'])} items")
                
            except Exception as e:
                logger.error(f"Error parsing health scores: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in health analysis: {str(e)}")
        
    return state

def create_recommendation_graph():
    """Create the LangGraph for recommendation flow."""
    # Create a new state graph
    graph = StateGraph(RecommendationState)
    
    # Add nodes
    graph.add_node("refine_query", refine_query_node)
    graph.add_node("generate_embedding", generate_embedding_node)
    graph.add_node("search_dishes", search_dishes_node)
    graph.add_node("rerank_results", rerank_results_node)
    graph.add_node("analyze_health", analyze_health_attributes_node)  # Add health analysis node
    
    # Define edges
    graph.add_edge("refine_query", "generate_embedding")
    graph.add_edge("generate_embedding", "search_dishes")
    graph.add_edge("search_dishes", "rerank_results")
    graph.add_edge("rerank_results", "analyze_health")  # Connect to health analysis
    
    # Set entry point
    graph.set_entry_point("refine_query")
    
    # Compile the graph
    return graph.compile()

# Create the recommendation graph
recommendation_graph = create_recommendation_graph()

async def process_recommendation(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Process a recommendation request using the LangGraph."""
    try:
        # Initial state
        initial_state: RecommendationState = {
            "original_query": query,
            "refined_query": None,
            "confidence": 0.0,
            "embedding": None,
            "recommendations": [],
            "top_k": top_k,
            "error": None
        }
        
        # Execute the graph
        result = await recommendation_graph.ainvoke(initial_state)
        
        # Clean up result for response
        response = {
            "original_query": result["original_query"],
            "refined_query": result["refined_query"],
            "confidence": result["confidence"],
            "recommendations": result["recommendations"],
            "processing_info": {
                "error": result.get("error")
            }
        }
        
        return response
    except Exception as e:
        logger.error(f"Error processing recommendation: {str(e)}")
        return {
            "original_query": query,
            "refined_query": None,
            "confidence": 0.0,
            "recommendations": [],
            "processing_info": {
                "error": f"Recommendation processing failed: {str(e)}"
            }
        }