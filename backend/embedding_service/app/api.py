"""API module for sending menu items to the menu service.

Defines MenuServiceClient, which can be injected for testability and modularity.
"""

import asyncio
from typing import List, Dict, Any
import aiohttp
from app.config import logger, settings


class MenuServiceClient:
    """Client for interacting with the menu service."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize the menu service client.

        Args:
            base_url: Base URL for the menu service
            timeout: Timeout for API requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def send_menu_items(self, menu_items: List[Dict[str, Any]]) -> bool:
        """Send menu items with embeddings to the menu service.

        Args:
            menu_items: List of menu items with embeddings

        Returns:
            True if at least one item was successfully sent, False otherwise
        """
        if not menu_items:
            logger.warning("No menu items to send")
            return True

        url = f"{self.base_url}/api/menu"
        success_count = 0

        try:
            logger.info("Sending %s menu items to database at %s", len(menu_items), url)

            # Process in batches for better performance
            async def send_batch(batch: List[Dict[str, Any]]) -> int:
                """Send a batch of menu items and return the number of successful sends."""
                successes = 0
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    tasks = []
                    for item in batch:
                        if "restaurant_id" not in item:
                            logger.warning(
                                "Missing restaurant_id for item: %s", item.get('name', 'unknown')
                            )
                            continue

                        # Debug log to see what's being sent
                        logger.debug(
                            "Sending item with restaurant_id: %s", item["restaurant_id"]
                        )
                        tasks.append(session.post(url, json=item))

                    responses = await asyncio.gather(*tasks, return_exceptions=True)

                    for response in responses:
                        if isinstance(response, Exception):
                            logger.error("Error sending menu item: %s", str(response))
                            continue

                        if response.status in [200, 201]:
                            successes += 1
                        else:
                            try:
                                error_text = await response.text()
                                logger.error(
                                    "Failed to send item: HTTP %s, %s",
                                    response.status,
                                    error_text,
                                )
                            except Exception:  # pylint: disable=broad-except
                                logger.error("Failed to send item: HTTP %s", response.status)

                return successes

            # Process in batches
            batch_size = 10
            batches = [menu_items[i:i + batch_size] for i in range(0, len(menu_items), batch_size)]

            for batch_num, batch in enumerate(batches):
                logger.info("Processing batch %s/%s", batch_num + 1, len(batches))
                success_count += await send_batch(batch)

            success_rate = success_count / len(menu_items) if menu_items else 1.0
            logger.info(
                "Sent %s/%s menu items (%s%%)",
                success_count,
                len(menu_items),
                int(success_rate * 100),
            )

            return success_count > 0

        except Exception as e:
            logger.error("Error sending menu items to database: %s", str(e))
            return False

menu_service_client = MenuServiceClient(settings.menu_service_url)


async def send_menu_items_with_embeddings(menu_items: List[Dict[str, Any]]) -> bool:
    """Send menu items with embeddings to the menu service.

    Args:
        menu_items: List of menu items with embeddings

    Returns:
        bool: True if at least one item was successfully sent, False otherwise
    """
    return await menu_service_client.send_menu_items(menu_items)
