from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer, DECIMAL, Date
from app.core.database import Base


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    exercise_type = Column(String(50))
    duration_min = Column(Integer)
    calories_burned = Column(DECIMAL(6, 1))
