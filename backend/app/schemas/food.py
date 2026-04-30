from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class FoodResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    calories_per_100g: Optional[Decimal]
    protein_g: Optional[Decimal]
    fat_g: Optional[Decimal]
    carbs_g: Optional[Decimal]
    fiber_g: Optional[Decimal]

    class Config:
        from_attributes = True
