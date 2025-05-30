import asyncio
from typing import Tuple, Optional
import google.generativeai as genai
from app.config import logger, GEMINI_API_KEY, CONFIDENCE_THRESHOLD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

REFINEMENT_PROMPT = """
You are an AI assistant for a food recommendation system. 
Your task is to refine user queries about food cravings into clearer, more specific descriptions that can be used for semantic search.

Examples:
- "I want something sweet" -> "Sweet dessert with rich flavors and satisfying texture"
- "Need spicy food" -> "Spicy dishes with bold flavors and aromatic spices"
- "Quick breakfast" -> "Quick and easy breakfast dishes that are nutritious and satisfying"

User Query: {query}

Please refine this query into a more detailed food description that will help find relevant dishes. 
Only include the refined query in your response, nothing else.

Also, provide an honest confidence score between 0 and 1 indicating how confident you are that your refinement captures the true intent:

Format your response exactly like this:
REFINED_QUERY: [your refined query]
CONFIDENCE: [0.0-1.0]
"""

ITERATIVE_REFINEMENT_PROMPT = """
You are an AI assistant for a food recommendation system. 
Your task is to further refine a food query that still needs improvement.

Original User Query: {original_query}
Current Refined Query: {current_query}
Current Confidence Score: {current_confidence}

Please improve this query even further to make it more specific, detailed, and useful for semantic food search.
The goal is to create the most accurate representation of the user's food preferences.

Enhance the query by:
- Adding more specific flavor details
- Including texture preferences
- Specifying dish types or categories when appropriate
- Adding contextual food elements

Only include the refined query in your response, nothing else.
Also, provide an honest confidence score between 0 and 1:
1.0 = Absolutely certain this refinement captures the user's intent perfectly
0.8 = Very confident in most aspects, but some minor uncertainty
0.6 = Moderately confident, captured main intent but may miss nuances
0.4 = Some confidence, but substantial uncertainty about specific preferences
0.2 = Low confidence, significant ambiguity in the original query
0.0 = Complete guesswork

Format your response exactly like this:
REFINED_QUERY: [your refined query]
CONFIDENCE: [0.0-1.0]
"""

async def refine_query(query: str, max_iterations: int = 100) -> Tuple[str, float]:
    """
    Refine the user query using LLM and return confidence score.
    Will iterate refinement until confidence threshold or max_iterations is reached.
    """
    current_query = query
    current_confidence = 0.0
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            # First refinement uses standard prompt
            if iteration == 1:
                prompt = REFINEMENT_PROMPT.format(query=query)
            # Subsequent refinements use iterative prompt if confidence is below threshold
            else:
                prompt = ITERATIVE_REFINEMENT_PROMPT.format(
                    original_query=query,
                    current_query=current_query,
                    current_confidence=current_confidence
                )
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            
            # Parse response
            text = response.text
            
            # Extract refined query and confidence
            refined_query = ""
            confidence = 0.0
            
            for line in text.split("\n"):
                if line.startswith("REFINED_QUERY:"):
                    refined_query = line.replace("REFINED_QUERY:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence_str = line.replace("CONFIDENCE:", "").strip()
                        confidence = float(confidence_str)
                    except ValueError:
                        confidence = 0.0
            
            # Default to previous values if parsing failed
            if not refined_query:
                refined_query = current_query
            if confidence <= 0:
                confidence = current_confidence
                
            # Update current values
            current_query = refined_query
            current_confidence = confidence
            
            # Check if we've reached sufficient confidence
            if current_confidence >= CONFIDENCE_THRESHOLD:
                logger.info(f"Query refinement reached sufficient confidence ({current_confidence:.2f}) after {iteration} iterations")
                break
                
        return current_query, current_confidence
            
    except Exception as e:
        logger.error(f"Error refining query: {str(e)}")
        # In case of error, return original query with low confidence
        return query, 1.0