from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.food import Food
from app.schemas.food import FoodResponse

router = APIRouter(prefix="/api/foods", tags=["食物库"])


@router.get("/search", response_model=list[FoodResponse])
def search_foods(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    return (
        db.query(Food)
        .filter(or_(Food.name.contains(q), Food.category.contains(q)))
        .limit(limit)
        .all()
    )
