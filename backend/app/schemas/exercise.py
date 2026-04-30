from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional


class ExerciseLogCreate(BaseModel):
    date: date
    exercise_type: str
    duration_min: int
    calories_burned: Optional[Decimal] = None


class ExerciseLogResponse(BaseModel):
    id: int
    date: date
    exercise_type: str
    duration_min: int
    calories_burned: Optional[Decimal]

    class Config:
        from_attributes = True
