from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.menu_items import MenuItemListResponse
from app.schemas.queries import QueryCreate
from app.repositories.repository import QueriesRepository, RecommendationRepository, MenuItemRepository, MenuItemAddonsRepository
from app.utils.recommend import resolve_query_gemini_top_k, resolve_query_gemini_threshold
from app.models.filters import GetMenuItemAddonsFilters
from app.schemas.recommendation import RecommendationCreate

router = APIRouter(prefix="/queries", tags=["queries"])

@router.post("/resolve", response_model=MenuItemListResponse)
def resolve_query(query: QueryCreate, db: Session = Depends(get_db)):
    try:
        queries_repo = QueriesRepository()
        menu_item_repo = MenuItemRepository()
        menu_item_addons_repo = MenuItemAddonsRepository()
        recommendation_repo = RecommendationRepository()

        query_obj = queries_repo.create(db, obj_in=query)

        menu_item_ids, context = resolve_query_gemini_top_k(db, user_id=query.user_id, query_text=query.query_text)
        # menu_item_ids, context = resolve_query_gemini_threshold(db, user_id=query.user_id, query_text=query.query_text)
        menu_items = []
        for mid in menu_item_ids:
            menu_item = menu_item_repo.get(db, id=mid)
            if menu_item:
                addons_filters = GetMenuItemAddonsFilters(menu_item_id=menu_item.id)
                addons = menu_item_addons_repo.get(db, filters=addons_filters)
                menu_item.addons = addons
                menu_items.append(menu_item)

        for mid in menu_item_ids:
            recommendation = RecommendationCreate(
                query_id=query_obj.id,
                menu_item_id=mid,
                confidence_score=context['confidences'].get(mid, 1.0),
                meta={}
            )
            recommendation_repo.create(db, obj_in=recommendation)

        return MenuItemListResponse(data=menu_items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 