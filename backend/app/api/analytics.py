from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.food import Food

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])


@router.get("/nutrition-trend")
def get_nutrition_trend(
    days: int = Query(30, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    end = date.today()
    start = end - timedelta(days=days)

    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == current_user.id, DailyLog.date >= start, DailyLog.date <= end)
        .all()
    )

    daily_data = {}
    for log in logs:
        d = log.date.isoformat()
        if d not in daily_data:
            daily_data[d] = {"date": d, "calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in log.items:
            factor = float(item.quantity_g) / 100
            if item.food_id:
                food = db.query(Food).filter(Food.id == item.food_id).first()
                if food:
                    daily_data[d]["calories"] += float(food.calories_per_100g or 0) * factor
                    daily_data[d]["protein"] += float(food.protein_g or 0) * factor
                    daily_data[d]["fat"] += float(food.fat_g or 0) * factor
                    daily_data[d]["carbs"] += float(food.carbs_g or 0) * factor
            elif item.ai_nutrition:
                daily_data[d]["calories"] += item.ai_nutrition.get("calories", 0)

    for v in daily_data.values():
        for k in ["calories", "protein", "fat", "carbs"]:
            v[k] = round(v[k], 1)

    return sorted(daily_data.values(), key=lambda x: x["date"])


@router.get("/weight-trend")
def get_weight_trend(
    days: int = Query(90, le=365),
    current_user: User = Depends(get_current_user),
):
    return {
        "current_weight": float(current_user.weight_kg) if current_user.weight_kg else None,
        "message": "体重趋势需要定期记录体重数据，目前仅显示当前体重",
    }
