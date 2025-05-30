import asyncio
import psycopg2
import psycopg2.extras
import json
from typing import List, Optional, Dict, Any
from app.config import logger, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, TOP_K

async def search_similar_dishes(embedding: List[float], top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Search for similar dishes in the database using cosine similarity."""
    if not embedding:
        logger.error("Empty embedding provided for search")
        return []
    
    try:
        # Connect to PostgreSQL
        conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        
        # Define as regular function, not async
        def _execute_query():
            try:
                with psycopg2.connect(conn_string) as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        # Import pgvector extension if not already
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                        
                        # Convert embedding to vector type using PostgreSQL's vector constructor
                        vector_placeholder = ", ".join(["%s"] * len(embedding))
                        vector_cast = f"CAST(ARRAY[{vector_placeholder}] AS vector)"
                        
                        # Query using cosine similarity with proper vector casting
                        query = f"""
                            SELECT mi.id, mi.name, mi.description, mi.price, mi.restaurant_id, 
                                   r.name as restaurant_name, mi.meta,
                                   1 - (mi.embedding <=> {vector_cast}) as similarity_score
                            FROM menu_items mi
                            JOIN restaurants r ON mi.restaurant_id = r.id
                            WHERE mi.is_active = true AND mi.embedding IS NOT NULL
                            ORDER BY mi.embedding <=> {vector_cast}
                            LIMIT %s
                        """
                        
                        # Create parameter list with embedding values twice (once for each vector_cast)
                        params = embedding + embedding + [top_k]
                        
                        # Execute query
                        cur.execute(query, params)
                        
                        results = cur.fetchall()
                        return [dict(row) for row in results]
            except Exception as e:
                logger.error(f"Database query error: {str(e)}")
                return []
                
        # Execute query in a thread pool
        results = await asyncio.to_thread(_execute_query)
        
        # Process results
        processed_results = []
        for item in results:
            try:
                # Skip None items
                if not item:
                    continue
                    
                # Extract category from meta if available
                meta = {}
                if "meta" in item and item["meta"] is not None:
                    meta_value = item["meta"]
                    if isinstance(meta_value, str):
                        try:
                            meta = json.loads(meta_value)
                        except Exception as e:
                            pass
                    elif isinstance(meta_value, dict):
                        meta = meta_value
                
                category = meta.get("category", "")
                
                processed_item = {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "description": item.get("description") or "",
                    "price": float(item.get("price", 0)),
                    "restaurant_id": item.get("restaurant_id", ""),
                    "restaurant_name": item.get("restaurant_name", ""),
                    "similarity_score": float(item.get("similarity_score", 0)),
                    "category": category
                }
                processed_results.append(processed_item)
            except Exception as e:
                logger.error(f"Error processing item: {str(e)}")
                continue
                
        return processed_results
        
    except Exception as e:
        logger.error(f"Vector search error: {str(e)}")
        return []

# Add this function to get database stats

async def get_cuisine_distribution(limit: int = 10) -> List[Dict[str, Any]]:
    """Get distribution of cuisines in the database."""
    try:
        # Connect to PostgreSQL
        conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        
        def _execute_query():
            try:
                with psycopg2.connect(conn_string) as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        # Get counts of menu items by restaurant
                        cur.execute("""
                            SELECT r.name as restaurant_name, COUNT(mi.id) as menu_count
                            FROM restaurants r
                            JOIN menu_items mi ON r.id = mi.restaurant_id
                            WHERE mi.is_active = true
                            GROUP BY r.name
                            ORDER BY menu_count DESC
                            LIMIT %s
                        """, (limit,))
                        
                        results = cur.fetchall()
                        return [dict(row) for row in results]
            except Exception as e:
                logger.error(f"Database query error: {str(e)}")
                return []
                
        # Execute query in a thread pool
        return await asyncio.to_thread(_execute_query)
        
    except Exception as e:
        logger.error(f"Error getting cuisine distribution: {str(e)}")
        return []