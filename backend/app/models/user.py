from sqlalchemy import Column, BigInteger, String, Enum, Date, DECIMAL, DateTime, func
from app.core.database import Base
import enum


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    avatar = Column(String(500))
    gender = Column(Enum(Gender))
    birthday = Column(Date)
    height_cm = Column(DECIMAL(5, 1))
    weight_kg = Column(DECIMAL(5, 1))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
