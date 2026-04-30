from sqlalchemy import Column, BigInteger, ForeignKey, String, Date, DateTime, JSON, func
from app.core.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    recommendation_type = Column(String(20), nullable=False)
    content = Column(JSON, default=dict)
    model_used = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
