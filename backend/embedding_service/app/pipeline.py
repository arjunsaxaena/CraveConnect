"""Pipeline module for processing menu images and extracting menu items with embeddings."""

import time
from typing import Tuple, List, Dict, Any

from app.embedding import generate_menu_item_embedding
from app.ocr import ocr_tool
from app.menu_extractor import menu_extractor
from app.api import send_menu_items_with_embeddings
from app.config import logger


class MenuProcessingPipeline:
    """Pipeline for processing menu images and extracting menu items with embeddings."""

    async def process(self, restaurant_id: str, image_data: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Process menu image and extract menu items with embeddings.

        Args:
            restaurant_id: ID of the restaurant
            image_data: Binary image data of the menu

        Returns:
            Tuple of (success, message, items)
        """
        try:
            # Step 1: Extract text from image
            menu_text = await self._extract_text_from_image(image_data)
            if not menu_text:
                return False, "Failed to extract text from menu image", []

            # Step 2: Extract menu items from text
            menu_items = await self._extract_menu_items(menu_text, restaurant_id)
            if not menu_items:
                return False, "No menu items extracted from text", []

            # Step 3: Generate embeddings for menu items
            items_with_embeddings = await self._generate_embeddings(menu_items)

            # Step 4: Send items to database
            success = await self._store_menu_items(items_with_embeddings)

            if not success:
                return True, "Menu processed but some items may not be stored", items_with_embeddings

            return True, "Successfully processed and stored menu", items_with_embeddings

        except Exception as e:
            logger.error("Error in menu processing pipeline: %s", str(e))
            return False, f"Error processing menu: {str(e)}", []

    async def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from menu image.

        Args:
            image_data: Binary image data

        Returns:
            Extracted text
        """
        if not ocr_tool:
            logger.warning("OCR tool not initialized")
            return ""

        try:
            logger.info("Starting OCR text extraction...")
            start_time = time.time()
            menu_text = await ocr_tool.extract_text(image_data)
            elapsed_time = time.time() - start_time

            if not menu_text:
                logger.warning("OCR extraction failed - no text extracted")
                return ""

            logger.info(
                "OCR extraction complete in %.2fs. Text length: %s",
                elapsed_time,
                len(menu_text)
            )
            return menu_text
        except Exception as e:
            logger.error("Text extraction error: %s", str(e))
            return ""

    async def _extract_menu_items(self, menu_text: str, restaurant_id: str) -> List[Dict[str, Any]]:
        """Extract menu items from text.

        Args:
            menu_text: Text extracted from menu image
            restaurant_id: ID of the restaurant

        Returns:
            List of extracted menu items
        """
        try:
            logger.info("Starting menu item extraction...")
            start_time = time.time()
            menu_items = await menu_extractor.extract_items(menu_text, restaurant_id)
            elapsed_time = time.time() - start_time

            if not menu_items:
                logger.warning("Menu item extraction failed - no items found")
                return []

            logger.info(
                "Menu item extraction complete in %.2fs. Items found: %s",
                elapsed_time,
                len(menu_items)
            )
            return menu_items
        except Exception as e:
            logger.error("Menu item extraction error: %s", str(e))
            return []

    async def _generate_embeddings(self, menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to menu items.

        Args:
            menu_items: List of menu items

        Returns:
            List of menu items with embeddings
        """
        if not menu_items:
            return []

        logger.info("Starting embedding generation for %s items...", len(menu_items))
        start_time = time.time()
        result = []

        for item in menu_items:
            try:
                embedding = await generate_menu_item_embedding(item)

                if embedding:
                    item["embedding"] = embedding

                result.append(item)

            except Exception as e:
                logger.error("Error adding embedding to menu item: %s", str(e))
                # Still add the item without embedding
                result.append(item)

        elapsed_time = time.time() - start_time
        logger.info("Embedding generation complete in %.2fs", elapsed_time)
        return result

    async def _store_menu_items(self, menu_items: List[Dict[str, Any]]) -> bool:
        """Store menu items in the database.

        Args:
            menu_items: List of menu items with embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Sending menu items to database...")
            start_time = time.time()

            success = await send_menu_items_with_embeddings(menu_items)

            elapsed_time = time.time() - start_time
            logger.info("Database storage complete in %.2fs", elapsed_time)

            return success
        except Exception as e:
            logger.error("Error storing menu items: %s", str(e))
            return False
        