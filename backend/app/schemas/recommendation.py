from pydantic import BaseModel
from datetime import date
from typing import Optional


class RecommendationResponse(BaseModel):
    id: int
    date: date
    recommendation_type: str
    content: dict
    model_used: Optional[str]

    class Config:
        from_attributes = True
