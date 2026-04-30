from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    avatar: Optional[str]
    gender: Optional[str]
    birthday: Optional[date]
    height_cm: Optional[Decimal]
    weight_kg: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
