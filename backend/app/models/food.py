from sqlalchemy import Column, BigInteger, String, DECIMAL, JSON
from app.core.database import Base


class Food(Base):
    __tablename__ = "food_database"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50))
    calories_per_100g = Column(DECIMAL(6, 1))
    protein_g = Column(DECIMAL(5, 1))
    fat_g = Column(DECIMAL(5, 1))
    carbs_g = Column(DECIMAL(5, 1))
    fiber_g = Column(DECIMAL(5, 1))
    vitamins = Column(JSON, default=dict)
    minerals = Column(JSON, default=dict)
    source = Column(String(50))
