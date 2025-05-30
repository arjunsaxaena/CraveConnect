import asyncio
import json
import re
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import logger, GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash',
                             generation_config={"temperature": 0.1, "top_p": 0.95})  # Lower temperature for more predictable outputs

RERANKING_PROMPT = """
You are helping re-rank food dish recommendations based on how precisely they match a user's query.
For each dish, assign a match score from 0-100 where:
- 100 = Perfect match for ALL aspects of the query
- 75 = Good match for most aspects
- 50 = Moderate match, satisfies some key aspects
- 25 = Weak match, minimally related
- 0 = Completely irrelevant

User Query: "{query}"

Dishes to evaluate:
{dishes}

Critical ranking factors (in order of importance):
1. HEALTH ALIGNMENT - If the query mentions health, nutrition, or dietary needs, this is the top priority
   - SEVERELY PENALIZE dishes with obvious unhealthy ingredients (e.g., excessive sugar, fried foods)
   - FAVOR dishes with fresh ingredients, vegetables, lean proteins
   
2. CUISINE TYPE MATCH - Does the dish match the specific cuisine type requested?

3. FLAVOR PROFILE MATCH - Does it have the specific flavors requested?

4. DIETARY RESTRICTIONS - Does it comply with mentioned restrictions (vegetarian, gluten-free, etc.)?

You MUST respond ONLY with a valid JSON array containing dish IDs and scores.
Do not include any explanations, notes or other text.

Example response format:
[
  {{"id": "abc123", "score": 85}},
  {{"id": "def456", "score": 45}}
]
"""

async def rerank_recommendations(query: str, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Re-rank recommendations based on semantic analysis of query and dishes."""
    if not recommendations:
        return []
        
    try:
        # Format dishes for the prompt
        dishes_text = ""
        for i, dish in enumerate(recommendations):
            dishes_text += f"{i+1}. ID: {dish['id']}, Name: {dish['name']}, " \
                          f"Description: {dish['description'] or ''}, " \
                          f"Category: {dish.get('category', '')}\n\n"
        
        # Generate reranking scores
        prompt = RERANKING_PROMPT.format(query=query, dishes=dishes_text)
        
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        # Extract JSON from response text
        text = response.text
        
        # Try to find JSON array in the response using regex
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                # Parse the extracted JSON
                scores = json.loads(json_str)
            except json.JSONDecodeError:
                # If parsing fails, assign default scores
                logger.error(f"Failed to parse JSON: {json_str}")
                for dish in recommendations:
                    dish["combined_score"] = dish["similarity_score"]
                return recommendations
        else:
            # If no JSON found, assign default scores
            logger.error("No JSON array found in model response")
            for dish in recommendations:
                dish["combined_score"] = dish["similarity_score"]
            return recommendations
        
        # Create ID to score mapping
        id_to_score = {item["id"]: item["score"] for item in scores if "id" in item and "score" in item}
        
        # Apply new scores and resort
        for dish in recommendations:
            if dish["id"] in id_to_score:
                # Combine vector similarity with semantic understanding
                # Weight LLM score more heavily (70/30 split)
                llm_score = id_to_score[dish["id"]] / 100
                vector_score = dish["similarity_score"]
                dish["original_score"] = vector_score
                dish["llm_score"] = llm_score
                dish["combined_score"] = (0.3 * vector_score) + (0.7 * llm_score)
            else:
                dish["combined_score"] = dish["similarity_score"]
        
        # Sort by combined score and remove duplicates
        deduped_results = []
        seen_names = set()
        
        for dish in sorted(recommendations, key=lambda x: x["combined_score"], reverse=True):
            # Simple deduplication by name
            if dish["name"] not in seen_names:
                seen_names.add(dish["name"])
                deduped_results.append(dish)
        
        # Add cuisine type to results
        for dish in deduped_results:
            # Add inferred cuisine type based on name/description
            if "Margherita" in dish["name"] or "Pizza" in dish["name"] or "Pepperoni" in dish["name"]:
                dish["cuisine_type"] = "Italian"
            elif "Sandwich" in dish["name"]:
                dish["cuisine_type"] = "American"
            elif "Paneer" in dish["name"]:
                dish["cuisine_type"] = "Indian"
            else:
                dish["cuisine_type"] = "Unknown"
                
        return deduped_results
        
    except Exception as e:
        logger.error(f"Error in reranking: {str(e)}")
        return recommendations  # Fall back to original recommendations

async def add_cuisine_context(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add cuisine context to each recommendation."""
    try:
        # Prepare batch of items for analysis
        items_for_analysis = []
        for dish in recommendations:
            items_for_analysis.append({
                "id": dish["id"],
                "name": dish["name"],
                "description": dish["description"]
            })
            
        if not items_for_analysis:
            return recommendations
            
        # Create prompt for cuisine analysis
        prompt = """
        For each food dish, identify its most likely cuisine type based on name and description.
        Return a JSON array with id and cuisine type. Format:
        [
          {"id": "dish_id_1", "cuisine": "Italian"},
          {"id": "dish_id_2", "cuisine": "Mexican"}
        ]
        
        Dishes:
        """
        
        for item in items_for_analysis:
            prompt += f"\n- ID: {item['id']}, Name: {item['name']}, Description: {item['description']}"
            
        # Generate cuisine analysis
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        # Parse response
        import json
        cuisines = json.loads(response.text)
        
        # Add cuisine info to recommendations
        id_to_cuisine = {item["id"]: item["cuisine"] for item in cuisines}
        for dish in recommendations:
            dish["cuisine_type"] = id_to_cuisine.get(dish["id"], "Unknown")
            
        return recommendations
            
    except Exception as e:
        logger.error(f"Error adding cuisine context: {str(e)}")
        return recommendations