from sqlalchemy import Column, BigInteger, ForeignKey, JSON, Date, Integer, DateTime, func
from app.core.database import Base


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    allergies = Column(JSON, default=list)
    diseases = Column(JSON, default=list)
    dietary_preferences = Column(JSON, default=list)
    menstrual_cycle_start = Column(Date)
    menstrual_cycle_length = Column(Integer)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
