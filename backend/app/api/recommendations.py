from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.ai_client import call_ai_api
from app.core.config import get_settings
from app.models.user import User
from app.models.health_profile import HealthProfile
from app.models.daily_log import DailyLog, LogItem
from app.models.food import Food
from app.models.exercise import ExerciseLog
from app.models.recommendation import AIRecommendation
from app.schemas.recommendation import RecommendationResponse

settings = get_settings()
router = APIRouter(prefix="/api/recommendations", tags=["AI推荐"])


def get_user_profile_text(user: User, profile: HealthProfile) -> str:
    from datetime import date as dt_date
    age = None
    if user.birthday:
        age = (dt_date.today() - user.birthday).days // 365
    bmi = None
    if user.height_cm and user.weight_kg:
        h = float(user.height_cm) / 100
        bmi = round(float(user.weight_kg) / (h * h), 1)

    lines = [
        f"- 性别：{'男' if user.gender == 'male' else '女' if user.gender == 'female' else '未设置'}",
        f"- 年龄：{age or '未设置'}",
        f"- 身高：{user.height_cm or '未设置'}cm，体重：{user.weight_kg or '未设置'}kg，BMI：{bmi or '未设置'}",
    ]

    if profile:
        if profile.diseases:
            lines.append(f"- 病史：{', '.join(profile.diseases)}")
        if profile.allergies:
            lines.append(f"- 过敏：{', '.join(profile.allergies)}")
        if profile.dietary_preferences:
            lines.append(f"- 饮食偏好：{', '.join(profile.dietary_preferences)}")
        if user.gender == 'female' and profile.menstrual_cycle_start:
            today = dt_date.today()
            days_since = (today - profile.menstrual_cycle_start).days
            cycle_len = profile.menstrual_cycle_length or 28
            day_in_cycle = days_since % cycle_len
            if day_in_cycle < 7:
                lines.append(f"- 生理期状态：经期中（第{day_in_cycle + 1}天）")
            elif day_in_cycle < 14:
                lines.append(f"- 生理期状态：卵泡期")
            else:
                lines.append(f"- 生理期状态：黄体期")

    return "\n".join(lines)


def get_nutrition_summary(db: Session, user_id: int) -> str:
    end = date.today()
    start = end - timedelta(days=7)
    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user_id, DailyLog.date >= start, DailyLog.date <= end)
        .all()
    )
    if not logs:
        return "近7天无饮食记录"

    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    days_with_data = set()

    for log in logs:
        days_with_data.add(log.date)
        for item in log.items:
            factor = float(item.quantity_g) / 100
            if item.food_id:
                food = db.query(Food).filter(Food.id == item.food_id).first()
                if food:
                    total_calories += float(food.calories_per_100g or 0) * factor
                    total_protein += float(food.protein_g or 0) * factor
                    total_fat += float(food.fat_g or 0) * factor
                    total_carbs += float(food.carbs_g or 0) * factor
            elif item.ai_nutrition:
                total_calories += item.ai_nutrition.get("calories", 0)

    days = len(days_with_data) or 1
    return (
        f"近{days}天平均每日摄入：\n"
        f"- 热量：{total_calories / days:.0f} kcal\n"
        f"- 蛋白质：{total_protein / days:.1f}g\n"
        f"- 脂肪：{total_fat / days:.1f}g\n"
        f"- 碳水化合物：{total_carbs / days:.1f}g"
    )


@router.post("/diet", response_model=RecommendationResponse)
async def generate_diet_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    profile_text = get_user_profile_text(current_user, profile or HealthProfile(user_id=current_user.id))
    nutrition_text = get_nutrition_summary(db, current_user.id)

    system_prompt = "你是一位专业的营养师，根据用户的个人健康信息和近期饮食数据，提供个性化的每日饮食建议。回复使用中文。"
    user_prompt = f"""请根据以下用户信息生成今日饮食方案：

【用户信息】
{profile_text}

【近7天饮食分析】
{nutrition_text}

请输出JSON格式（不要包含markdown代码块标记）：
{{
  "breakfast": [{{"name": "菜品名", "amount": "分量", "calories": 热量数值}}],
  "lunch": [{{"name": "菜品名", "amount": "分量", "calories": 热量数值}}],
  "dinner": [{{"name": "菜品名", "amount": "分量", "calories": 热量数值}}],
  "nutrients_to补充": ["营养素1", "营养素2"],
  "foods_to_avoid": ["食物1", "食物2"],
  "reason": "简要原因说明"
}}"""

    import json
    content_text = await call_ai_api(system_prompt, user_prompt)
    try:
        content = json.loads(content_text)
    except json.JSONDecodeError:
        content = {"raw_response": content_text}

    rec = AIRecommendation(
        user_id=current_user.id,
        date=date.today(),
        recommendation_type="diet",
        content=content,
        model_used=settings.AI_MODEL,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.post("/exercise", response_model=RecommendationResponse)
async def generate_exercise_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    profile_text = get_user_profile_text(current_user, profile or HealthProfile(user_id=current_user.id))

    end = date.today()
    start = end - timedelta(days=7)
    exercises = (
        db.query(ExerciseLog)
        .filter(ExerciseLog.user_id == current_user.id, ExerciseLog.date >= start, ExerciseLog.date <= end)
        .all()
    )
    if exercises:
        total_min = sum(e.duration_min or 0 for e in exercises)
        exercise_summary = f"近7天运动{len(exercises)}次，共{total_min}分钟"
    else:
        exercise_summary = "近7天无运动记录"

    system_prompt = "你是一位专业的运动康复师，根据用户的健康信息和运动习惯，提供个性化的运动建议。回复使用中文。"
    user_prompt = f"""请根据以下用户信息生成运动建议：

【用户信息】
{profile_text}

【运动习惯】
{exercise_summary}

请输出JSON格式（不要包含markdown代码块标记）：
{{
  "recommended_exercises": [{{"name": "运动项目", "duration": "时长", "intensity": "强度", "benefit": "益处"}}],
  "avoid_exercises": ["需避免的运动"],
  "precautions": ["注意事项"],
  "weekly_goal": "每周运动目标建议"
}}"""

    import json
    content_text = await call_ai_api(system_prompt, user_prompt)
    try:
        content = json.loads(content_text)
    except json.JSONDecodeError:
        content = {"raw_response": content_text}

    rec = AIRecommendation(
        user_id=current_user.id,
        date=date.today(),
        recommendation_type="exercise",
        content=content,
        model_used=settings.AI_MODEL,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/history", response_model=list[RecommendationResponse])
def get_recommendation_history(
    rec_type: str = Query(None, alias="type"),
    limit: int = Query(30, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AIRecommendation).filter(AIRecommendation.user_id == current_user.id)
    if rec_type:
        query = query.filter(AIRecommendation.recommendation_type == rec_type)
    return query.order_by(AIRecommendation.date.desc()).limit(limit).all()
