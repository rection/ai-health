from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal


class LogItemCreate(BaseModel):
    food_id: Optional[int] = None
    quantity_g: Decimal
    custom_name: Optional[str] = None


class LogItemResponse(BaseModel):
    id: int
    food_id: Optional[int]
    quantity_g: Decimal
    custom_name: Optional[str]
    ai_nutrition: Optional[dict]
    food_name: Optional[str] = None
    calories: Optional[float] = None

    class Config:
        from_attributes = True


class DailyLogCreate(BaseModel):
    date: date
    meal_type: str


class DailyLogResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    items: List[LogItemResponse] = []
    total_calories: float = 0

    class Config:
        from_attributes = True
