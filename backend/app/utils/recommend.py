from sqlalchemy.orm import Session
from app.repositories.repository import (
    MenuItemEmbeddingRepository,
    MenuItemRepository,
    UserPreferencesRepository,
    FavoritesRepository,
    OrderRepository,
)
import google.generativeai as genai
from app.core.config import settings
from app.models.filters import GetMenuItemFilters, GetUserPreferencesFilters, GetFavoritesFilters, GetOrderFilters

if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    raise RuntimeError("GEMINI_API_KEY not found in settings")

def get_user_profile(db: Session, user_id: str):
    prefs_repo = UserPreferencesRepository()
    fav_repo = FavoritesRepository()
    order_repo = OrderRepository()
    menu_repo = MenuItemRepository()

    prefs_filters = GetUserPreferencesFilters(user_id=user_id)
    prefs_list = prefs_repo.get(db, filters=prefs_filters)
    prefs = prefs_list[0] if prefs_list else None

    fav_filters = GetFavoritesFilters(user_id=user_id)
    favorites = fav_repo.get(db, filters=fav_filters)

    order_filters = GetOrderFilters(user_id=user_id)
    orders = order_repo.get(db, filters=order_filters)

    ordered_names = set()
    for order in orders:
        meta = getattr(order, 'meta', {}) or {}
        items = meta.get('items', [])
        for item in items:
            name = item.get('name')
            if name:
                ordered_names.add(name.lower())

    ordered_menu_item_ids = set()
    if ordered_names:
        menu_items = menu_repo.get(db)
        for mi in menu_items:
            if mi.name and mi.name.lower() in ordered_names:
                ordered_menu_item_ids.add(str(mi.id))

    return {
        "preferences": prefs,
        "favorite_menu_item_ids": {str(f.menu_item_id) for f in favorites},
        "ordered_menu_item_ids": ordered_menu_item_ids,
    }

def get_menu_item_details(db: Session, menu_item_ids):
    menu_repo = MenuItemRepository()
    filters = GetMenuItemFilters()
    filters.id = menu_item_ids
    items = menu_repo.get(db, filters=filters)
    return {str(item.id): item for item in items}

def compute_boost(menu_item, user_profile):
    boost = 0.0
    prefs = user_profile["preferences"]
    if not prefs:
        return boost

    cuisines = getattr(prefs, 'preferred_cuisines', [])
    if cuisines and menu_item.meta and menu_item.meta.get("cuisine") in cuisines:
        boost += 0.2

    restrictions = getattr(prefs, 'dietary_restrictions', [])
    if restrictions and menu_item.tags:
        if any(dr in menu_item.tags for dr in restrictions):
            boost += 0.1

    spice = getattr(prefs, 'spice_tolerance', None)
    if spice and menu_item.meta and menu_item.meta.get("spice_level") == spice:
        boost += 0.1

    if str(menu_item.id) in user_profile["favorite_menu_item_ids"]:
        boost += 0.3

    if str(menu_item.id) in user_profile["ordered_menu_item_ids"]:
        boost += 0.1
    return boost

def is_suitable(menu_item, user_profile):
    prefs = user_profile["preferences"]
    if not prefs:
        return True

    allergies = getattr(prefs, 'allergies', [])
    if allergies and menu_item.allergens:
        if any(allergy in menu_item.allergens for allergy in allergies):
            return False

    restrictions = getattr(prefs, 'dietary_restrictions', [])
    if restrictions and menu_item.tags:
        if any(dr in menu_item.tags for dr in restrictions):
            return False
    return True

def resolve_query_gemini_top_k(db: Session, user_id: str, query_text: str, k: int = 5):
    response = genai.embed_content(
        model="models/embedding-001",
        content=query_text,
        task_type="RETRIEVAL_QUERY"
    )
    query_embedding = response['embedding']

    embedding_repo = MenuItemEmbeddingRepository()
    top_n = embedding_repo.get_top_k_similar(db, query_embedding, k=30)
    menu_item_ids = [mid for mid, _ in top_n]
    menu_items = get_menu_item_details(db, menu_item_ids)
    user_profile = get_user_profile(db, user_id)

    scored_items = []
    for mid, sim_score in top_n:
        item = menu_items.get(str(mid))
        if not item or not is_suitable(item, user_profile):
            continue
        boost = compute_boost(item, user_profile)
        final_score = sim_score + boost
        scored_items.append((mid, final_score))

    scored_items.sort(key=lambda x: x[1], reverse=True)
    top_k = scored_items[:k]
    confidences = {str(mid): float(score) for mid, score in top_k}
    menu_item_ids = [str(mid) for mid, _ in top_k]

    return menu_item_ids, {"confidences": confidences, "method": "embedding_similarity+personalization"}

def resolve_query_gemini_threshold(db: Session, user_id: str, query_text: str, threshold: float = 0.5):
    response = genai.embed_content(
        model="models/embedding-001",
        content=query_text,
        task_type="RETRIEVAL_QUERY"
    )
    query_embedding = response['embedding']

    embedding_repo = MenuItemEmbeddingRepository()
    top_n = embedding_repo.get_top_k_similar(db, query_embedding, k=30)
    menu_item_ids = [mid for mid, _ in top_n]
    menu_items = get_menu_item_details(db, menu_item_ids)
    user_profile = get_user_profile(db, user_id)

    scored_items = []
    for mid, sim_score in top_n:
        item = menu_items.get(str(mid))
        if not item or not is_suitable(item, user_profile):
            continue
        boost = compute_boost(item, user_profile)
        final_score = sim_score + boost
        scored_items.append((mid, final_score))

    filtered_items = [(mid, score) for mid, score in scored_items if score >= threshold]
    filtered_items.sort(key=lambda x: x[1], reverse=True)
    confidences = {str(mid): float(score) for mid, score in filtered_items}
    menu_item_ids = [str(mid) for mid, _ in filtered_items]

    return menu_item_ids, {"confidences": confidences, "method": "embedding_similarity+personalization", "threshold": threshold}
