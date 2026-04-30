from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.daily_log import DailyLog, LogItem
from app.models.food import Food
from app.models.user import User
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse, LogItemCreate, LogItemResponse

router = APIRouter(prefix="/api/daily-logs", tags=["饮食日志"])


@router.get("", response_model=list[DailyLogResponse])
def get_daily_logs(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(DailyLog)
        .options(joinedload(DailyLog.items))
        .filter(
            DailyLog.user_id == current_user.id,
            DailyLog.date >= start_date,
            DailyLog.date <= end_date,
        )
        .order_by(DailyLog.date.desc(), DailyLog.meal_type)
        .all()
    )
    results = []
    for log in logs:
        items = []
        total_cal = 0
        for item in log.items:
            food_name = None
            calories = None
            if item.food_id:
                food = db.query(Food).filter(Food.id == item.food_id).first()
                if food:
                    food_name = food.name
                    calories = float(food.calories_per_100g or 0) * float(item.quantity_g) / 100
            elif item.ai_nutrition:
                calories = item.ai_nutrition.get("calories", 0)
                food_name = item.custom_name
            total_cal += calories or 0
            items.append(LogItemResponse(
                id=item.id,
                food_id=item.food_id,
                quantity_g=item.quantity_g,
                custom_name=item.custom_name,
                ai_nutrition=item.ai_nutrition,
                food_name=food_name,
                calories=calories,
            ))
        results.append(DailyLogResponse(
            id=log.id,
            date=log.date,
            meal_type=log.meal_type,
            items=items,
            total_calories=total_cal,
        ))
    return results


@router.post("", response_model=DailyLogResponse)
def create_daily_log(
    data: DailyLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = DailyLog(user_id=current_user.id, date=data.date, meal_type=data.meal_type)
    db.add(log)
    db.commit()
    db.refresh(log)
    return DailyLogResponse(id=log.id, date=log.date, meal_type=log.meal_type, items=[], total_calories=0)


@router.post("/{log_id}/items", response_model=LogItemResponse)
def add_log_item(
    log_id: int,
    data: LogItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    item = LogItem(
        daily_log_id=log_id,
        food_id=data.food_id,
        quantity_g=data.quantity_g,
        custom_name=data.custom_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    food_name = None
    calories = None
    if item.food_id:
        food = db.query(Food).filter(Food.id == item.food_id).first()
        if food:
            food_name = food.name
            calories = float(food.calories_per_100g or 0) * float(item.quantity_g) / 100

    return LogItemResponse(
        id=item.id,
        food_id=item.food_id,
        quantity_g=item.quantity_g,
        custom_name=item.custom_name,
        ai_nutrition=item.ai_nutrition,
        food_name=food_name,
        calories=calories,
    )


@router.delete("/{log_id}/items/{item_id}")
def delete_log_item(
    log_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    item = db.query(LogItem).filter(LogItem.id == item_id, LogItem.daily_log_id == log_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="条目不存在")

    db.delete(item)
    db.commit()
    return {"message": "已删除"}
