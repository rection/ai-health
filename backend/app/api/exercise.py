from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.exercise import ExerciseLog
from app.models.user import User
from app.schemas.exercise import ExerciseLogCreate, ExerciseLogResponse

router = APIRouter(prefix="/api/exercise-logs", tags=["运动记录"])


@router.get("", response_model=list[ExerciseLogResponse])
def get_exercise_logs(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ExerciseLog)
        .filter(
            ExerciseLog.user_id == current_user.id,
            ExerciseLog.date >= start_date,
            ExerciseLog.date <= end_date,
        )
        .order_by(ExerciseLog.date.desc())
        .all()
    )


@router.post("", response_model=ExerciseLogResponse)
def create_exercise_log(
    data: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = ExerciseLog(user_id=current_user.id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
