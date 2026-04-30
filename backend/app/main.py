from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, users, health, foods, daily_logs, exercise, recommendations, analytics
from app.core.database import SessionLocal
from app.seeds.seed_foods import seed_foods

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)
app.include_router(daily_logs.router)
app.include_router(exercise.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_foods(db)
    finally:
        db.close()
