from sqlalchemy import Column, BigInteger, ForeignKey, Date, String, DECIMAL, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("LogItem", back_populates="daily_log", cascade="all, delete-orphan")


class LogItem(Base):
    __tablename__ = "log_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    daily_log_id = Column(BigInteger, ForeignKey("daily_logs.id"), nullable=False)
    food_id = Column(BigInteger, ForeignKey("food_database.id"), nullable=True)
    quantity_g = Column(DECIMAL(6, 1), nullable=False)
    custom_name = Column(String(100))
    ai_nutrition = Column(JSON, default=dict)

    daily_log = relationship("DailyLog", back_populates="items")
