"""Module for post-processing extracted menu items.

This module provides the MenuItemPostProcessor class, which is responsible for refining and normalizing
menu items after extraction. It can be injected as a dependency for better testability and modularity.
"""

import re
from typing import List, Dict, Any, Set
from app.config import logger


class MenuItemPostProcessor:
    """Post-processor for refining extracted menu items.

    This class can be injected as a dependency to decouple post-processing logic from extraction.
    """

    def __init__(self):
        """Initialize the post-processor."""
        # No initialization needed

    def process_items(self, items: List[Dict[str, Any]], menu_text: str) -> List[Dict[str, Any]]:
        """Process and refine extracted menu items.

        Args:
            items: List of extracted menu items
            menu_text: Original menu text for context

        Returns:
            Processed menu items
        """
        if not items:
            return []

        # Apply processing steps in sequence
        items = self._separate_name_description(items)
        base_name_groups = self._group_by_base_name(items)
        items = self._assign_sizes(items, base_name_groups, menu_text)
        items = self._validate_prices(items, base_name_groups)

        return items

    def _validate_prices(
        self, items: List[Dict[str, Any]], groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Validate and correct suspicious price values."""
        # Find average price by category to use as reference
        category_prices = {}
        for item in items:
            if not item.get("price") or item["price"] == 0:
                continue

            category = item.get("category", "unknown")
            if category not in category_prices:
                category_prices[category] = []

            category_prices[category].append(item["price"])

        # Calculate average prices per category
        category_avg = {
            cat: sum(prices) / len(prices) for cat, prices in category_prices.items() if prices
        }

        # Fix suspicious prices
        for item in items:
            # First ensure price is a number
            if item.get("price") is None:
                item["price"] = 0

            # Check if price is suspicious
            if item.get("price", 0) <= 0:
                logger.warning(
                    "Suspicious price detected for %s: %s", item["name"], item.get("price")
                )

                # Try to infer from items with same base name
                base_name = self._clean_item_name(item["name"])
                if base_name in groups:
                    valid_prices = [
                        i["price"] for i in groups[base_name] if i.get("price", 0) > 0
                    ]
                    if valid_prices:
                        item["price"] = max(valid_prices)
                        item["price_inferred"] = True
                        logger.info(
                            "Price inferred for %s: %s from similar items",
                            item["name"],
                            item["price"],
                        )
                        continue

                # Try to infer from category average
                category = item.get("category", "unknown")
                if category in category_avg:
                    item["price"] = round(category_avg[category])
                    item["price_inferred"] = True
                    logger.info(
                        "Price inferred for %s: %s from category average",
                        item["name"],
                        item["price"],
                    )
                else:
                    # Flag for manual review if can't infer
                    item["requires_price_review"] = True
                    logger.warning(
                        "Item %s flagged for manual price review", item["name"]
                    )

        return items

    def _separate_name_description(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Separate name and description where they are combined.

        Args:
            items: List of menu items

        Returns:
            Items with separated name and description
        """
        for item in items:
            if not item.get("name"):
                continue

            name = item["name"]
            desc_match = re.search(r'\(([^)]+)\)$', name)
            if desc_match:
                extracted_desc = desc_match.group(1).strip()

                if not item.get("description") or not item["description"].strip():
                    item["description"] = extracted_desc

                item["name"] = re.sub(r'\s*\([^)]+\)$', '', name).strip()

        return items

    def _group_by_base_name(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by their base name to identify size variants.

        Args:
            items: List of menu items

        Returns:
            Dict mapping base names to lists of items
        """
        groups = {}

        for item in items:
            if not item.get("name"):
                continue

            base_name = self._clean_item_name(item["name"])

            if base_name not in groups:
                groups[base_name] = []

            groups[base_name].append(item)

        # Only return groups with multiple items (potential size variants)
        return {name: items for name, items in groups.items() if len(items) > 1}

    def _clean_item_name(self, name: str) -> str:
        """Clean item name by removing size information.

        Args:
            name: Item name

        Returns:
            Cleaned name without size information
        """
        # Remove text in parentheses
        name = re.sub(r'\s*\([^)]*\)', '', name)

        # Remove size words
        name = re.sub(r'\b(small|medium|large|regular|half|full)\b', '', name, flags=re.IGNORECASE)

        # Remove single letter sizes
        name = re.sub(r'\b[SML]\b', '', name)

        # Remove measurements
        name = re.sub(
            r'\b\d+(\.\d+)?\s*(oz|inch|"|\'|cm)\b',
            '',
            name,
            flags=re.IGNORECASE
        )

        return name.strip()

    def _assign_sizes(
        self,
        items: List[Dict[str, Any]],
        groups: Dict[str, List[Dict[str, Any]]],
        menu_text: str
    ) -> List[Dict[str, Any]]:
        """Assign size information to grouped items.

        Args:
            items: List of all menu items
            groups: Grouped items by base name
            menu_text: Original menu text

        Returns:
            Items with size information added
        """
        if not groups:
            return items

        size_indicators = self._extract_size_indicators(menu_text)

        if size_indicators:
            logger.info("Found size indicators: %s", size_indicators)

            for _, group_items in groups.items():
                # Sort by price to ensure consistent size assignment
                group_items.sort(key=lambda x: x.get("price", 0))

                if len(group_items) <= len(size_indicators):
                    for i, item in enumerate(group_items):
                        item["size"] = size_indicators[i]
                else:
                    self._assign_generic_sizes(group_items)
        else:
            # If no size indicators found, use generic sizing for all groups
            for _, group_items in groups.items():
                group_items.sort(key=lambda x: x.get("price", 0))
                self._assign_generic_sizes(group_items)

        return items

    def _extract_size_indicators(self, menu_text: str) -> List[str]:
        """Extract size indicators from menu text.

        Args:
            menu_text: Original menu text

        Returns:
            List of size indicators
        """
        # Try to find inch-based sizes (e.g., "S 10", "M 12", "L 14")
        inch_pattern = re.compile(r'([SML])\s*(\d+)["\']', re.IGNORECASE)
        inch_matches = inch_pattern.findall(menu_text)
        if inch_matches and len(inch_matches) >= 2:
            return [f"{m[0]} {m[1]}\"" for m in inch_matches]

        # Try to find pure inch sizes
        inches_pattern = re.compile(r'(\d+)["\']', re.IGNORECASE)
        inch_numbers = inches_pattern.findall(menu_text)
        if inch_numbers and len(inch_numbers) >= 2:
            inch_numbers = sorted([int(x) for x in inch_numbers if x.isdigit()])
            return [f"{x}\"" for x in inch_numbers]

        # Try to find word-based sizes (Small, Medium, Large, etc.)
        size_words_pattern = re.compile(
            r'\b(Small|Medium|Large|Regular|Half|Full)\b',
            re.IGNORECASE
        )
        size_words = size_words_pattern.findall(menu_text)
        if size_words and len(set(size_words)) >= 2:
            # Standardize capitalization
            size_map = {
                "small": "Small", "medium": "Medium", "large": "Large",
                "regular": "Regular", "half": "Half", "full": "Full"
            }

            # Get unique sizes preserving order
            seen: Set[str] = set()
            unique_sizes = [
                size_map.get(word.lower(), word) for word in size_words
                if not (word.lower() in seen or seen.add(word.lower()))
            ]

            if len(unique_sizes) >= 2:
                return unique_sizes

        # No consistent size indicators found
        return []

    def _assign_generic_sizes(self, items: List[Dict[str, Any]]) -> None:
        """Assign generic size names based on the number of items.

        Args:
            items: List of menu items from the same group
        """
        if not items:
            return

        # Choose appropriate size names based on count
        if len(items) == 2:
            size_names = ["Regular", "Large"]
        elif len(items) == 3:
            size_names = ["Small", "Medium", "Large"]
        else:
            size_names = ["Small", "Medium", "Large", "Extra Large", "Family", "Party"]
            # Extend if needed
            while len(size_names) < len(items):
                size_names.append(f"Size {len(size_names) + 1}")

        # Assign sizes
        for i, item in enumerate(items):
            if i < len(size_names):
                item["size"] = size_names[i]
                