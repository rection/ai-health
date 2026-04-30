from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class HealthProfileUpdate(BaseModel):
    allergies: Optional[List[str]] = None
    diseases: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    menstrual_cycle_start: Optional[date] = None
    menstrual_cycle_length: Optional[int] = None


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    allergies: List[str]
    diseases: List[str]
    dietary_preferences: List[str]
    menstrual_cycle_start: Optional[date]
    menstrual_cycle_length: Optional[int]

    class Config:
        from_attributes = True
