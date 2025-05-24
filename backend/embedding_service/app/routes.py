from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.schemas import MenuItemEmbeddingRequest, EmbeddingResponse, BatchEmbeddingRequest, BatchEmbeddingResponse
from app.embedding import generate_embedding, generate_menu_item_embedding
from app.api import update_menu_item_embedding, get_menu_item
from app.config import logger
from typing import Dict, List, Any
import asyncio

router = APIRouter()

@router.post("/generate-embedding", response_model=EmbeddingResponse)
async def create_embedding(request: MenuItemEmbeddingRequest, background_tasks: BackgroundTasks):
    """
    Generate embedding for a menu item.
    
    This endpoint will:
    1. Generate an embedding vector for the menu item
    2. Return the embedding vector
    
    If a menu_item_id is provided, it will also update the menu item in the database
    as a background task.
    """
    try:
        menu_item = request.menu_item.dict()
        menu_item_id = menu_item.get("id")
        
        # Generate embedding
        embedding = generate_menu_item_embedding(menu_item)
        
        if not embedding:
            return EmbeddingResponse(
                success=False,
                menu_item_id=menu_item_id,
                error="Failed to generate embedding"
            )
        
        # If menu_item_id is provided, schedule update in background
        if menu_item_id:
            background_tasks.add_task(
                update_menu_item_embedding,
                menu_item_id,
                embedding
            )
        
        return EmbeddingResponse(
            success=True,
            menu_item_id=menu_item_id,
            embedding=embedding[:10] if len(embedding) > 10 else embedding,  # Truncated for display
            full_embedding=embedding  # Full embedding for storage
        )
    
    except Exception as e:
        logger.error(f"Error processing embedding request: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return EmbeddingResponse(
            success=False,
            error=str(e)
        )

@router.post("/generate-embeddings-batch", response_model=BatchEmbeddingResponse)
async def create_embeddings_batch(request: BatchEmbeddingRequest):
    """
    Generate embeddings for multiple menu items in a batch.
    
    This is more efficient for processing multiple items at once.
    If menu_item_id is provided, it will also update the menu item in the database.
    """
    results = []
    success_count = 0
    failure_count = 0
    
    try:
        for menu_item in request.menu_items:
            menu_item_dict = menu_item.dict()
            menu_item_id = menu_item_dict.get("id")
            
            # Generate embedding
            embedding = generate_menu_item_embedding(menu_item_dict)
            
            if not embedding:
                results.append({
                    "id": menu_item_id,
                    "success": False,
                    "error": "Failed to generate embedding"
                })
                failure_count += 1
                continue
            
            # Update the menu item with its embedding if ID is provided
            if menu_item_id:
                update_success = update_menu_item_embedding(menu_item_id, embedding)
                
                if update_success:
                    results.append({
                        "id": menu_item_id,
                        "success": True,
                        "embedding": embedding[:10] if len(embedding) > 10 else embedding,
                        "full_embedding": embedding
                    })
                    success_count += 1
                else:
                    results.append({
                        "id": menu_item_id,
                        "success": False,
                        "error": "Failed to update menu item with embedding"
                    })
                    failure_count += 1
            else:
                # No ID provided, just return the embedding
                results.append({
                    "id": None,
                    "success": True,
                    "embedding": embedding[:10] if len(embedding) > 10 else embedding,
                    "full_embedding": embedding
                })
                success_count += 1
        
        return BatchEmbeddingResponse(
            results=results,
            success_count=success_count,
            failure_count=failure_count
        )
    
    except Exception as e:
        logger.error(f"Error processing batch embedding request: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/generate-embedding-by-id/{menu_item_id}", response_model=EmbeddingResponse)
async def generate_embedding_by_id(menu_item_id: str, background_tasks: BackgroundTasks):
    """
    Fetch a menu item by ID and generate its embedding.
    
    This is useful for generating embeddings for existing menu items.
    """
    try:
        # Fetch the menu item from the database
        menu_item = get_menu_item(menu_item_id)
        
        if not menu_item:
            return EmbeddingResponse(
                success=False,
                menu_item_id=menu_item_id,
                error="Menu item not found"
            )
        
        # Generate embedding
        embedding = generate_menu_item_embedding(menu_item)
        
        if not embedding:
            return EmbeddingResponse(
                success=False,
                menu_item_id=menu_item_id,
                error="Failed to generate embedding"
            )
        
        # Schedule the update task in the background
        background_tasks.add_task(
            update_menu_item_embedding,
            menu_item_id,
            embedding
        )
        
        return EmbeddingResponse(
            success=True,
            menu_item_id=menu_item_id,
            embedding=embedding[:10] if len(embedding) > 10 else embedding,  # Truncated for display
            full_embedding=embedding  # Full embedding for storage
        )
    
    except Exception as e:
        logger.error(f"Error generating embedding for menu item {menu_item_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return EmbeddingResponse(
            success=False,
            menu_item_id=menu_item_id,
            error=str(e)
        ) 