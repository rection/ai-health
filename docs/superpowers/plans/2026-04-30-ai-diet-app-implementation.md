# AI 饮食应用实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于大模型的个性化 AI 饮食管理 Web 应用，支持用户健康档案、饮食日志、AI 饮食/运动推荐、数据分析。

**Architecture:** 前后端分离架构，Vue 3 前端 + FastAPI 后端 + MySQL 数据库 + Redis 缓存 + 大模型 API 推荐引擎。

**Tech Stack:** Vue 3, Element Plus, Pinia, ECharts, Axios, FastAPI, SQLAlchemy, MySQL, Redis, JWT, Claude/OpenAI API

---

## 第一阶段：后端基础设施

### Task 1: 项目初始化与依赖配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/.env.example`

- [ ] **Step 1: 创建项目目录结构**

```bash
mkdir -p backend/app/{api,core,models,schemas,seeds}
```

- [ ] **Step 2: 编写 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pymysql==1.1.1
alembic==1.13.0
redis==5.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pydantic==2.9.0
pydantic-settings==2.5.0
httpx==0.27.0
python-dotenv==1.0.1
```

- [ ] **Step 3: 编写核心配置 app/core/config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI Diet"
    DEBUG: bool = True

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "ai_diet"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI
    AI_API_KEY: str = ""
    AI_API_BASE: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: 编写 .env.example**

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_diet

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=your-secret-key-change-in-production
AI_API_KEY=sk-your-api-key
AI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4o
```

- [ ] **Step 5: 编写 FastAPI 入口 app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
```

- [ ] **Step 6: 创建 __init__.py 文件**

```bash
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/api/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
```

- [ ] **Step 7: 验证启动**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Expected: 访问 http://localhost:8000/api/health 返回 `{"status":"ok","app":"AI Diet"}`

---

### Task 2: 数据库连接与 ORM 模型

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/health_profile.py`
- Create: `backend/app/models/food.py`
- Create: `backend/app/models/daily_log.py`
- Create: `backend/app/models/exercise.py`
- Create: `backend/app/models/recommendation.py`

- [ ] **Step 1: 编写数据库连接 core/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 编写 User 模型 models/user.py**

```python
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
```

- [ ] **Step 3: 编写 HealthProfile 模型 models/health_profile.py**

```python
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
```

- [ ] **Step 4: 编写 Food 模型 models/food.py**

```python
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
```

- [ ] **Step 5: 编写 DailyLog 和 LogItem 模型 models/daily_log.py**

```python
from sqlalchemy import Column, BigInteger, ForeignKey, Date, String, DECIMAL, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


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
```

- [ ] **Step 6: 编写 ExerciseLog 模型 models/exercise.py**

```python
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
```

- [ ] **Step 7: 编写 AIRecommendation 模型 models/recommendation.py**

```python
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
```

---

### Task 3: Alembic 数据库迁移配置

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/.gitkeep`

- [ ] **Step 1: 初始化 alembic**

```bash
cd backend
alembic init alembic
```

- [ ] **Step 2: 修改 alembic/env.py 连接配置**

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import get_settings
from app.core.database import Base
import app.models

settings = get_settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: 生成并执行迁移**

```bash
cd backend
alembic revision --autogenerate -m "initial tables"
alembic upgrade head
```

Expected: 所有表创建成功

---

### Task 4: 安全模块 - JWT 与密码

**Files:**
- Create: `backend/app/core/security.py`

- [ ] **Step 1: 编写 security.py**

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

---

## 第二阶段：后端 API

### Task 5: 认证 API - 注册与登录

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/api/auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 Pydantic 模型 schemas/user.py**

```python
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
```

- [ ] **Step 2: 编写认证路由 api/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
```

- [ ] **Step 3: 注册路由到 main.py**

在 `app/main.py` 中添加：

```python
from app.api import auth

app.include_router(auth.router)
```

---

### Task 6: 用户 API - 个人信息管理

**Files:**
- Create: `backend/app/api/users.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写用户路由 api/users.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
```

- [ ] **Step 2: 注册路由到 main.py**

```python
from app.api import auth, users

app.include_router(auth.router)
app.include_router(users.router)
```

---

### Task 7: 健康档案 API

**Files:**
- Create: `backend/app/schemas/health.py`
- Create: `backend/app/api/health.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 Pydantic 模型 schemas/health.py**

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class HealthProfileUpdate(BaseModel):
    allergies: Optional[List[str]] = None
    diseases: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    menstrual_cycle_start: Optional[date] = None
    menstrual_cycle_length: Optional[int] = None


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    allergies: List[str]
    diseases: List[str]
    dietary_preferences: List[str]
    menstrual_cycle_start: Optional[date]
    menstrual_cycle_length: Optional[int]

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 编写健康档案路由 api/health.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.health_profile import HealthProfile
from app.models.user import User
from app.schemas.health import HealthProfileUpdate, HealthProfileResponse

router = APIRouter(prefix="/api/health-profile", tags=["健康档案"])


@router.get("", response_model=HealthProfileResponse)
def get_health_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=HealthProfileResponse)
def update_health_profile(
    data: HealthProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
```

- [ ] **Step 3: 注册路由到 main.py**

```python
from app.api import auth, users, health

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
```

---

### Task 8: 食物库搜索 API

**Files:**
- Create: `backend/app/schemas/food.py`
- Create: `backend/app/api/foods.py`
- Create: `backend/app/seeds/seed_foods.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 Pydantic 模型 schemas/food.py**

```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class FoodResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    calories_per_100g: Optional[Decimal]
    protein_g: Optional[Decimal]
    fat_g: Optional[Decimal]
    carbs_g: Optional[Decimal]
    fiber_g: Optional[Decimal]

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 编写食物搜索路由 api/foods.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.food import Food
from app.schemas.food import FoodResponse

router = APIRouter(prefix="/api/foods", tags=["食物库"])


@router.get("/search", response_model=list[FoodResponse])
def search_foods(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    return (
        db.query(Food)
        .filter(or_(Food.name.contains(q), Food.category.contains(q)))
        .limit(limit)
        .all()
    )
```

- [ ] **Step 3: 编写种子数据 seeds/seed_foods.py**

```python
FOODS = [
    {"name": "米饭(蒸)", "category": "主食", "calories_per_100g": 116, "protein_g": 2.6, "fat_g": 0.3, "carbs_g": 25.6, "fiber_g": 0.3, "source": "中国食物成分表"},
    {"name": "面条(煮)", "category": "主食", "calories_per_100g": 110, "protein_g": 3.5, "fat_g": 0.5, "carbs_g": 22.8, "fiber_g": 0.5, "source": "中国食物成分表"},
    {"name": "馒头", "category": "主食", "calories_per_100g": 221, "protein_g": 7.0, "fat_g": 1.1, "carbs_g": 44.2, "fiber_g": 1.3, "source": "中国食物成分表"},
    {"name": "全麦面包", "category": "主食", "calories_per_100g": 246, "protein_g": 12.3, "fat_g": 3.4, "carbs_g": 41.3, "fiber_g": 6.0, "source": "USDA"},
    {"name": "燕麦片", "category": "主食", "calories_per_100g": 379, "protein_g": 13.5, "fat_g": 6.7, "carbs_g": 67.7, "fiber_g": 10.6, "source": "USDA"},
    {"name": "鸡胸肉", "category": "肉类", "calories_per_100g": 133, "protein_g": 31.0, "fat_g": 1.2, "carbs_g": 0, "fiber_g": 0, "source": "USDA"},
    {"name": "鸡蛋(煮)", "category": "蛋类", "calories_per_100g": 155, "protein_g": 12.6, "fat_g": 10.6, "carbs_g": 1.1, "fiber_g": 0, "source": "USDA"},
    {"name": "牛肉(瘦)", "category": "肉类", "calories_per_100g": 125, "protein_g": 22.2, "fat_g": 3.0, "carbs_g": 0, "fiber_g": 0, "source": "中国食物成分表"},
    {"name": "猪肉(瘦)", "category": "肉类", "calories_per_100g": 143, "protein_g": 20.3, "fat_g": 6.2, "carbs_g": 1.5, "fiber_g": 0, "source": "中国食物成分表"},
    {"name": "三文鱼", "category": "水产", "calories_per_100g": 139, "protein_g": 20.4, "fat_g": 6.3, "carbs_g": 0, "fiber_g": 0, "source": "USDA"},
    {"name": "虾仁", "category": "水产", "calories_per_100g": 48, "protein_g": 10.4, "fat_g": 0.2, "carbs_g": 0, "fiber_g": 0, "source": "中国食物成分表"},
    {"name": "豆腐", "category": "豆制品", "calories_per_100g": 81, "protein_g": 8.1, "fat_g": 3.7, "carbs_g": 4.2, "fiber_g": 0.4, "source": "中国食物成分表"},
    {"name": "牛奶(全脂)", "category": "乳制品", "calories_per_100g": 65, "protein_g": 3.2, "fat_g": 3.6, "carbs_g": 4.8, "fiber_g": 0, "source": "USDA"},
    {"name": "西兰花", "category": "蔬菜", "calories_per_100g": 34, "protein_g": 2.8, "fat_g": 0.4, "carbs_g": 6.6, "fiber_g": 2.6, "source": "USDA"},
    {"name": "番茄", "category": "蔬菜", "calories_per_100g": 18, "protein_g": 0.9, "fat_g": 0.2, "carbs_g": 3.9, "fiber_g": 1.2, "source": "USDA"},
    {"name": "黄瓜", "category": "蔬菜", "calories_per_100g": 15, "protein_g": 0.7, "fat_g": 0.1, "carbs_g": 2.9, "fiber_g": 0.5, "source": "中国食物成分表"},
    {"name": "菠菜", "category": "蔬菜", "calories_per_100g": 23, "protein_g": 2.9, "fat_g": 0.4, "carbs_g": 3.6, "fiber_g": 2.2, "source": "USDA"},
    {"name": "苹果", "category": "水果", "calories_per_100g": 52, "protein_g": 0.3, "fat_g": 0.2, "carbs_g": 13.8, "fiber_g": 2.4, "source": "USDA"},
    {"name": "香蕉", "category": "水果", "calories_per_100g": 89, "protein_g": 1.1, "fat_g": 0.3, "carbs_g": 22.8, "fiber_g": 2.6, "source": "USDA"},
    {"name": "橙子", "category": "水果", "calories_per_100g": 47, "protein_g": 0.9, "fat_g": 0.1, "carbs_g": 11.8, "fiber_g": 2.4, "source": "USDA"},
]


def seed_foods(db):
    from app.models.food import Food
    count = db.query(Food).count()
    if count > 0:
        return
    for food_data in FOODS:
        db.add(Food(**food_data))
    db.commit()
    print(f"Seeded {len(FOODS)} foods")
```

- [ ] **Step 4: 注册路由和种子数据到 main.py**

```python
from app.api import auth, users, health, foods
from app.core.database import SessionLocal
from app.seeds.seed_foods import seed_foods

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_foods(db)
    finally:
        db.close()
```

---

### Task 9: 饮食日志 API

**Files:**
- Create: `backend/app/schemas/daily_log.py`
- Create: `backend/app/api/daily_logs.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 Pydantic 模型 schemas/daily_log.py**

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal


class LogItemCreate(BaseModel):
    food_id: Optional[int] = None
    quantity_g: Decimal
    custom_name: Optional[str] = None


class LogItemResponse(BaseModel):
    id: int
    food_id: Optional[int]
    quantity_g: Decimal
    custom_name: Optional[str]
    ai_nutrition: Optional[dict]
    food_name: Optional[str] = None
    calories: Optional[float] = None

    class Config:
        from_attributes = True


class DailyLogCreate(BaseModel):
    date: date
    meal_type: str


class DailyLogResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    items: List[LogItemResponse] = []
    total_calories: float = 0

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 编写饮食日志路由 api/daily_logs.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.daily_log import DailyLog, LogItem
from app.models.food import Food
from app.models.user import User
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse, LogItemCreate, LogItemResponse

router = APIRouter(prefix="/api/daily-logs", tags=["饮食日志"])


@router.get("", response_model=list[DailyLogResponse])
def get_daily_logs(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(DailyLog)
        .options(joinedload(DailyLog.items))
        .filter(
            DailyLog.user_id == current_user.id,
            DailyLog.date >= start_date,
            DailyLog.date <= end_date,
        )
        .order_by(DailyLog.date.desc(), DailyLog.meal_type)
        .all()
    )
    results = []
    for log in logs:
        items = []
        total_cal = 0
        for item in log.items:
            food_name = None
            calories = None
            if item.food_id:
                food = db.query(Food).filter(Food.id == item.food_id).first()
                if food:
                    food_name = food.name
                    calories = float(food.calories_per_100g or 0) * float(item.quantity_g) / 100
            elif item.ai_nutrition:
                calories = item.ai_nutrition.get("calories", 0)
                food_name = item.custom_name
            total_cal += calories or 0
            items.append(LogItemResponse(
                id=item.id,
                food_id=item.food_id,
                quantity_g=item.quantity_g,
                custom_name=item.custom_name,
                ai_nutrition=item.ai_nutrition,
                food_name=food_name,
                calories=calories,
            ))
        results.append(DailyLogResponse(
            id=log.id,
            date=log.date,
            meal_type=log.meal_type,
            items=items,
            total_calories=total_cal,
        ))
    return results


@router.post("", response_model=DailyLogResponse)
def create_daily_log(
    data: DailyLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = DailyLog(user_id=current_user.id, date=data.date, meal_type=data.meal_type)
    db.add(log)
    db.commit()
    db.refresh(log)
    return DailyLogResponse(id=log.id, date=log.date, meal_type=log.meal_type, items=[], total_calories=0)


@router.post("/{log_id}/items", response_model=LogItemResponse)
def add_log_item(
    log_id: int,
    data: LogItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    item = LogItem(
        daily_log_id=log_id,
        food_id=data.food_id,
        quantity_g=data.quantity_g,
        custom_name=data.custom_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    food_name = None
    calories = None
    if item.food_id:
        food = db.query(Food).filter(Food.id == item.food_id).first()
        if food:
            food_name = food.name
            calories = float(food.calories_per_100g or 0) * float(item.quantity_g) / 100

    return LogItemResponse(
        id=item.id,
        food_id=item.food_id,
        quantity_g=item.quantity_g,
        custom_name=item.custom_name,
        ai_nutrition=item.ai_nutrition,
        food_name=food_name,
        calories=calories,
    )


@router.delete("/{log_id}/items/{item_id}")
def delete_log_item(
    log_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    item = db.query(LogItem).filter(LogItem.id == item_id, LogItem.daily_log_id == log_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="条目不存在")

    db.delete(item)
    db.commit()
    return {"message": "已删除"}
```

- [ ] **Step 3: 注册路由到 main.py**

```python
from app.api import auth, users, health, foods, daily_logs

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)
app.include_router(daily_logs.router)
```

---

### Task 10: 运动记录 API

**Files:**
- Create: `backend/app/schemas/exercise.py`
- Create: `backend/app/api/exercise.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 Pydantic 模型 schemas/exercise.py**

```python
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional


class ExerciseLogCreate(BaseModel):
    date: date
    exercise_type: str
    duration_min: int
    calories_burned: Optional[Decimal] = None


class ExerciseLogResponse(BaseModel):
    id: int
    date: date
    exercise_type: str
    duration_min: int
    calories_burned: Optional[Decimal]

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 编写运动记录路由 api/exercise.py**

```python
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
```

- [ ] **Step 3: 注册路由到 main.py**

```python
from app.api import auth, users, health, foods, daily_logs, exercise

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)
app.include_router(daily_logs.router)
app.include_router(exercise.router)
```

---

### Task 11: AI 推荐引擎

**Files:**
- Create: `backend/app/core/ai_client.py`
- Create: `backend/app/api/recommendations.py`
- Create: `backend/app/schemas/recommendation.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写 AI 客户端 core/ai_client.py**

```python
import httpx
from app.core.config import get_settings

settings = get_settings()


async def call_ai_api(system_prompt: str, user_prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.AI_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

- [ ] **Step 2: 编写 Pydantic 模型 schemas/recommendation.py**

```python
from pydantic import BaseModel
from datetime import date
from typing import Optional


class RecommendationResponse(BaseModel):
    id: int
    date: date
    recommendation_type: str
    content: dict
    model_used: Optional[str]

    class Config:
        from_attributes = True
```

- [ ] **Step 3: 编写推荐路由 api/recommendations.py**

```python
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
```

- [ ] **Step 4: 注册路由到 main.py**

```python
from app.api import auth, users, health, foods, daily_logs, exercise, recommendations

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)
app.include_router(daily_logs.router)
app.include_router(exercise.router)
app.include_router(recommendations.router)
```

---

### Task 12: 数据分析 API

**Files:**
- Create: `backend/app/api/analytics.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 编写数据分析路由 api/analytics.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.daily_log import DailyLog, LogItem
from app.models.food import Food
from app.models.exercise import ExerciseLog

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])


@router.get("/nutrition-trend")
def get_nutrition_trend(
    days: int = Query(30, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    end = date.today()
    start = end - timedelta(days=days)

    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == current_user.id, DailyLog.date >= start, DailyLog.date <= end)
        .all()
    )

    daily_data = {}
    for log in logs:
        d = log.date.isoformat()
        if d not in daily_data:
            daily_data[d] = {"date": d, "calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in log.items:
            factor = float(item.quantity_g) / 100
            if item.food_id:
                food = db.query(Food).filter(Food.id == item.food_id).first()
                if food:
                    daily_data[d]["calories"] += float(food.calories_per_100g or 0) * factor
                    daily_data[d]["protein"] += float(food.protein_g or 0) * factor
                    daily_data[d]["fat"] += float(food.fat_g or 0) * factor
                    daily_data[d]["carbs"] += float(food.carbs_g or 0) * factor
            elif item.ai_nutrition:
                daily_data[d]["calories"] += item.ai_nutrition.get("calories", 0)

    for v in daily_data.values():
        for k in ["calories", "protein", "fat", "carbs"]:
            v[k] = round(v[k], 1)

    return sorted(daily_data.values(), key=lambda x: x["date"])


@router.get("/weight-trend")
def get_weight_trend(
    days: int = Query(90, le=365),
    current_user: User = Depends(get_current_user),
):
    return {
        "current_weight": float(current_user.weight_kg) if current_user.weight_kg else None,
        "message": "体重趋势需要定期记录体重数据，目前仅显示当前体重",
    }
```

- [ ] **Step 2: 注册路由到 main.py**

最终 main.py 的路由注册部分：

```python
from app.api import auth, users, health, foods, daily_logs, exercise, recommendations, analytics

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(foods.router)
app.include_router(daily_logs.router)
app.include_router(exercise.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
```

---

## 第三阶段：前端

### Task 13: 前端项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/api/request.ts`

- [ ] **Step 1: 创建 Vue 3 项目**

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install element-plus @element-plus/icons-vue vue-router@4 pinia axios echarts vue-echarts dayjs
```

- [ ] **Step 2: 编写 API 请求封装 src/api/request.ts**

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
```

- [ ] **Step 3: 编写路由配置 src/router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/auth/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/auth/Register.vue') },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/dashboard/Dashboard.vue') },
      { path: 'diet-log', name: 'DietLog', component: () => import('../views/diet-log/DietLog.vue') },
      { path: 'health', name: 'Health', component: () => import('../views/health/HealthProfile.vue') },
      { path: 'exercise', name: 'Exercise', component: () => import('../views/exercise/ExerciseLog.vue') },
      { path: 'ai', name: 'AI', component: () => import('../views/ai/AIRecommend.vue') },
      { path: 'analytics', name: 'Analytics', component: () => import('../views/analytics/Analytics.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && to.name !== 'Register' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 4: 编写 Pinia 状态管理 src/stores/user.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export interface UserInfo {
  id: number
  username: string
  email: string | null
  avatar: string | null
  gender: string | null
  birthday: string | null
  height_cm: number | null
  weight_kg: number | null
}

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await request.get('/users/me')
    } catch {
      logout()
    }
  }

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, fetchUser, setToken, logout }
})
```

- [ ] **Step 5: 编写 Vite 配置 vite.config.ts 添加代理**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 6: 创建目录结构**

```bash
mkdir -p frontend/src/{views/{auth,dashboard,diet-log,health,exercise,ai,analytics},layouts,stores,components}
```

---

### Task 14: 登录注册页面

**Files:**
- Create: `frontend/src/views/auth/Login.vue`
- Create: `frontend/src/views/auth/Register.vue`

- [ ] **Step 1: 编写登录页 Login.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 style="text-align: center">AI 饮食助手</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">登录</el-button>
        </el-form-item>
        <div style="text-align: center">
          <el-link @click="$router.push('/register')">没有账号？去注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import request from '../../api/request'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res: any = await request.post('/auth/login', form)
    userStore.setToken(res.access_token)
    userStore.user = res.user
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
}
</style>
```

- [ ] **Step 2: 编写注册页 Register.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 style="text-align: center">注册账号</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名（3-50字符）" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（选填）" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleRegister">注册</el-button>
        </el-form-item>
        <div style="text-align: center">
          <el-link @click="$router.push('/login')">已有账号？去登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import request from '../../api/request'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '', email: '' })
const rules: FormRules = {
  username: [{ required: true, min: 3, max: 50, message: '用户名3-50字符', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
}

async function handleRegister() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res: any = await request.post('/auth/register', form)
    userStore.setToken(res.access_token)
    userStore.user = res.user
    ElMessage.success('注册成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
}
</style>
```

---

### Task 15: 主布局与导航

**Files:**
- Create: `frontend/src/layouts/MainLayout.vue`

- [ ] **Step 1: 编写主布局 MainLayout.vue**

```vue
<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div style="padding: 20px; text-align: center; color: #fff; font-size: 18px; font-weight: bold">
        AI 饮食助手
      </div>
      <el-menu :default-active="route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/diet-log">
          <el-icon><EditPen /></el-icon>
          <span>饮食记录</span>
        </el-menu-item>
        <el-menu-item index="/health">
          <el-icon><User /></el-icon>
          <span>健康档案</span>
        </el-menu-item>
        <el-menu-item index="/exercise">
          <el-icon><Trophy /></el-icon>
          <span>运动记录</span>
        </el-menu-item>
        <el-menu-item index="/ai">
          <el-icon><MagicStick /></el-icon>
          <span>AI 推荐</span>
        </el-menu-item>
        <el-menu-item index="/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; align-items: center; justify-content: flex-end; border-bottom: 1px solid #eee">
        <el-dropdown @command="handleCommand">
          <span style="cursor: pointer">
            {{ userStore.user?.username || '用户' }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main style="background: #f0f2f5; padding: 20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  HomeFilled, EditPen, User, Trophy,
  MagicStick, DataAnalysis, ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>
```

---

### Task 16: 仪表盘页面

**Files:**
- Create: `frontend/src/views/dashboard/Dashboard.vue`

- [ ] **Step 1: 编写仪表盘 Dashboard.vue**

```vue
<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card>
          <template #header>今日热量</template>
          <div style="font-size: 28px; font-weight: bold; color: #409EFF">{{ todayCalories }} kcal</div>
          <div style="color: #999; margin-top: 8px">推荐摄入 2000 kcal</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>今日记录</template>
          <div style="font-size: 28px; font-weight: bold; color: #67C23A">{{ todayMeals }} 餐</div>
          <div style="color: #999; margin-top: 8px">早餐/午餐/晚餐/加餐</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>本周运动</template>
          <div style="font-size: 28px; font-weight: bold; color: #E6A23C">{{ weekExercise }} 次</div>
          <div style="color: #999; margin-top: 8px">坚持运动，健康生活</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>本周营养趋势</template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>AI 今日建议</template>
          <div v-if="aiTip" style="white-space: pre-line; line-height: 1.8">{{ aiTip }}</div>
          <el-button v-else type="primary" @click="getAITip">获取 AI 建议</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../api/request'
import dayjs from 'dayjs'

const todayCalories = ref(0)
const todayMeals = ref(0)
const weekExercise = ref(0)
const aiTip = ref('')
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

async function loadDashboard() {
  const today = dayjs().format('YYYY-MM-DD')
  const weekAgo = dayjs().subtract(7, 'day').format('YYYY-MM-DD')

  try {
    const logs: any = await request.get('/daily-logs', { params: { start_date: today, end_date: today } })
    todayMeals.value = logs.length
    todayCalories.value = logs.reduce((sum: number, log: any) => sum + (log.total_calories || 0), 0)

    const exercises: any = await request.get('/exercise-logs', { params: { start_date: weekAgo, end_date: today } })
    weekExercise.value = exercises.length

    const trend: any = await request.get('/analytics/nutrition-trend', { params: { days: 7 } })
    renderChart(trend)
  } catch {}
}

function renderChart(data: any[]) {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['热量(kcal)', '蛋白质(g)', '脂肪(g)', '碳水(g)'] },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '热量(kcal)', type: 'line', data: data.map(d => d.calories) },
      { name: '蛋白质(g)', type: 'line', data: data.map(d => d.protein) },
      { name: '脂肪(g)', type: 'line', data: data.map(d => d.fat) },
      { name: '碳水(g)', type: 'line', data: data.map(d => d.carbs) },
    ],
  })
}

async function getAITip() {
  try {
    const res: any = await request.post('/recommendations/diet')
    aiTip.value = JSON.stringify(res.content, null, 2)
  } catch {}
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
})
</script>
```

---

### Task 17: 饮食记录页面

**Files:**
- Create: `frontend/src/views/diet-log/DietLog.vue`

- [ ] **Step 1: 编写饮食记录 DietLog.vue**

```vue
<template>
  <div>
    <el-card style="margin-bottom: 20px">
      <el-date-picker v-model="selectedDate" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" @change="loadLogs" />
    </el-card>

    <el-row :gutter="20">
      <el-col :span="6" v-for="meal in meals" :key="meal.type">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>{{ meal.label }}</span>
              <el-button type="primary" size="small" @click="openAddDialog(meal.type)">添加</el-button>
            </div>
          </template>
          <div v-if="getLogByMeal(meal.type)?.items?.length">
            <div v-for="item in getLogByMeal(meal.type)!.items" :key="item.id" style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between">
              <div>
                <div>{{ item.food_name || item.custom_name }}</div>
                <div style="color: #999; font-size: 12px">{{ item.quantity_g }}g</div>
              </div>
              <div style="display: flex; align-items: center; gap: 8px">
                <span style="color: #E6A23C">{{ item.calories?.toFixed(0) }} kcal</span>
                <el-button type="danger" size="small" link @click="deleteItem(getLogByMeal(meal.type)!.id, item.id)">删除</el-button>
              </div>
            </div>
            <div style="text-align: right; margin-top: 10px; font-weight: bold">
              合计: {{ getLogByMeal(meal.type)!.total_calories.toFixed(0) }} kcal
            </div>
          </div>
          <el-empty v-else description="暂无记录" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialogVisible" title="添加食物" width="500px">
      <el-form :model="addForm">
        <el-form-item label="搜索食物">
          <el-select v-model="addForm.food_id" filterable remote :remote-method="searchFoods" placeholder="输入食物名称搜索" style="width: 100%">
            <el-option v-for="food in foodOptions" :key="food.id" :label="`${food.name} (${food.calories_per_100g}kcal/100g)`" :value="food.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="或自定义食物">
          <el-input v-model="addForm.custom_name" placeholder="输入食物名称" />
        </el-form-item>
        <el-form-item label="食用量(g)">
          <el-input-number v-model="addForm.quantity_g" :min="1" :max="5000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addItem">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const logs = ref<any[]>([])
const dialogVisible = ref(false)
const currentMealType = ref('')
const foodOptions = ref<any[]>([])

const meals = [
  { type: 'breakfast', label: '早餐' },
  { type: 'lunch', label: '午餐' },
  { type: 'dinner', label: '晚餐' },
  { type: 'snack', label: '加餐' },
]

const addForm = reactive({
  food_id: null as number | null,
  quantity_g: 100,
  custom_name: '',
})

function getLogByMeal(type: string) {
  return logs.value.find(l => l.meal_type === type)
}

async function loadLogs() {
  logs.value = await request.get('/daily-logs', {
    params: { start_date: selectedDate.value, end_date: selectedDate.value },
  })
}

async function searchFoods(query: string) {
  if (!query) return
  foodOptions.value = await request.get('/foods/search', { params: { q: query } })
}

async function openAddDialog(mealType: string) {
  currentMealType.value = mealType
  addForm.food_id = null
  addForm.quantity_g = 100
  addForm.custom_name = ''
  foodOptions.value = []

  let log = getLogByMeal(mealType)
  if (!log) {
    log = await request.post('/daily-logs', { date: selectedDate.value, meal_type: mealType })
    await loadLogs()
  }
  dialogVisible.value = true
}

async function addItem() {
  const log = getLogByMeal(currentMealType.value)
  if (!log) return
  if (!addForm.food_id && !addForm.custom_name) {
    ElMessage.warning('请选择食物或输入自定义名称')
    return
  }
  await request.post(`/daily-logs/${log.id}/items`, {
    food_id: addForm.food_id,
    quantity_g: addForm.quantity_g,
    custom_name: addForm.custom_name || null,
  })
  dialogVisible.value = false
  ElMessage.success('添加成功')
  await loadLogs()
}

async function deleteItem(logId: number, itemId: number) {
  await request.delete(`/daily-logs/${logId}/items/${itemId}`)
  ElMessage.success('删除成功')
  await loadLogs()
}

onMounted(loadLogs)
</script>
```

---

### Task 18: 健康档案页面

**Files:**
- Create: `frontend/src/views/health/HealthProfile.vue`

- [ ] **Step 1: 编写健康档案 HealthProfile.vue**

```vue
<template>
  <el-card>
    <template #header>个人健康档案</template>
    <el-form :model="form" label-width="120px" style="max-width: 600px">
      <el-form-item label="身高(cm)">
        <el-input-number v-model="form.height_cm" :min="50" :max="250" :precision="1" />
      </el-form-item>
      <el-form-item label="体重(kg)">
        <el-input-number v-model="form.weight_kg" :min="20" :max="300" :precision="1" />
      </el-form-item>
      <el-form-item label="生日">
        <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="性别">
        <el-radio-group v-model="form.gender">
          <el-radio value="male">男</el-radio>
          <el-radio value="female">女</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="病史">
        <el-select v-model="form.diseases" multiple filterable allow-create placeholder="选择或输入病史" style="width: 100%">
          <el-option label="糖尿病" value="糖尿病" />
          <el-option label="高血压" value="高血压" />
          <el-option label="高血脂" value="高血脂" />
          <el-option label="痛风" value="痛风" />
          <el-option label="心脏病" value="心脏病" />
          <el-option label="肾病" value="肾病" />
          <el-option label="胃病" value="胃病" />
        </el-select>
      </el-form-item>
      <el-form-item label="过敏信息">
        <el-select v-model="form.allergies" multiple filterable allow-create placeholder="选择或输入过敏原" style="width: 100%">
          <el-option label="花生" value="花生" />
          <el-option label="牛奶" value="牛奶" />
          <el-option label="鸡蛋" value="鸡蛋" />
          <el-option label="海鲜" value="海鲜" />
          <el-option label="小麦" value="小麦" />
          <el-option label="大豆" value="大豆" />
        </el-select>
      </el-form-item>
      <el-form-item label="饮食偏好">
        <el-select v-model="form.dietary_preferences" multiple placeholder="选择饮食偏好" style="width: 100%">
          <el-option label="素食" value="素食" />
          <el-option label="低碳水" value="低碳水" />
          <el-option label="高蛋白" value="高蛋白" />
          <el-option label="低脂" value="低脂" />
          <el-option label="无糖" value="无糖" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="form.gender === 'female'" label="生理期开始">
        <el-date-picker v-model="form.menstrual_cycle_start" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item v-if="form.gender === 'female'" label="周期天数">
        <el-input-number v-model="form.menstrual_cycle_length" :min="21" :max="40" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import request from '../../api/request'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)

const form = reactive({
  height_cm: null as number | null,
  weight_kg: null as number | null,
  birthday: null as string | null,
  gender: null as string | null,
  diseases: [] as string[],
  allergies: [] as string[],
  dietary_preferences: [] as string[],
  menstrual_cycle_start: null as string | null,
  menstrual_cycle_length: 28,
})

onMounted(async () => {
  await userStore.fetchUser()
  if (userStore.user) {
    form.height_cm = userStore.user.height_cm as any
    form.weight_kg = userStore.user.weight_kg as any
    form.birthday = userStore.user.birthday
    form.gender = userStore.user.gender
  }
  try {
    const profile: any = await request.get('/health-profile')
    form.diseases = profile.diseases || []
    form.allergies = profile.allergies || []
    form.dietary_preferences = profile.dietary_preferences || []
    form.menstrual_cycle_start = profile.menstrual_cycle_start
    form.menstrual_cycle_length = profile.menstrual_cycle_length || 28
  } catch {}
})

async function save() {
  saving.value = true
  try {
    await request.put('/users/me', {
      height_cm: form.height_cm,
      weight_kg: form.weight_kg,
      birthday: form.birthday,
      gender: form.gender,
    })
    await request.put('/health-profile', {
      diseases: form.diseases,
      allergies: form.allergies,
      dietary_preferences: form.dietary_preferences,
      menstrual_cycle_start: form.menstrual_cycle_start,
      menstrual_cycle_length: form.menstrual_cycle_length,
    })
    await userStore.fetchUser()
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}
</script>
```

---

### Task 19: 运动记录页面

**Files:**
- Create: `frontend/src/views/exercise/ExerciseLog.vue`

- [ ] **Step 1: 编写运动记录 ExerciseLog.vue**

```vue
<template>
  <div>
    <el-card style="margin-bottom: 20px">
      <template #header>添加运动记录</template>
      <el-form :model="form" inline>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="运动类型">
          <el-select v-model="form.exercise_type" filterable allow-create>
            <el-option label="跑步" value="跑步" />
            <el-option label="快走" value="快走" />
            <el-option label="游泳" value="游泳" />
            <el-option label="骑车" value="骑车" />
            <el-option label="瑜伽" value="瑜伽" />
            <el-option label="力量训练" value="力量训练" />
            <el-option label="跳绳" value="跳绳" />
            <el-option label="篮球" value="篮球" />
            <el-option label="羽毛球" value="羽毛球" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input-number v-model="form.duration_min" :min="1" :max="480" />
        </el-form-item>
        <el-form-item label="消耗(kcal)">
          <el-input-number v-model="form.calories_burned" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addExercise">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>运动记录</template>
      <el-table :data="exercises" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="exercise_type" label="运动类型" />
        <el-table-column prop="duration_min" label="时长(分钟)" />
        <el-table-column prop="calories_burned" label="消耗(kcal)" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const exercises = ref<any[]>([])
const form = reactive({
  date: dayjs().format('YYYY-MM-DD'),
  exercise_type: '',
  duration_min: 30,
  calories_burned: 0,
})

async function loadExercises() {
  const today = dayjs().format('YYYY-MM-DD')
  const monthAgo = dayjs().subtract(30, 'day').format('YYYY-MM-DD')
  exercises.value = await request.get('/exercise-logs', {
    params: { start_date: monthAgo, end_date: today },
  })
}

async function addExercise() {
  if (!form.exercise_type) {
    ElMessage.warning('请选择运动类型')
    return
  }
  await request.post('/exercise-logs', form)
  ElMessage.success('添加成功')
  form.exercise_type = ''
  form.duration_min = 30
  form.calories_burned = 0
  await loadExercises()
}

onMounted(loadExercises)
</script>
```

---

### Task 20: AI 推荐页面

**Files:**
- Create: `frontend/src/views/ai/AIRecommend.vue`

- [ ] **Step 1: 编写 AI 推荐 AIRecommend.vue**

```vue
<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>饮食推荐</span>
              <el-button type="primary" :loading="dietLoading" @click="getDietRecommend">获取推荐</el-button>
            </div>
          </template>
          <div v-if="dietResult">
            <el-collapse>
              <el-collapse-item title="早餐" name="1">
                <div v-for="item in dietResult.content?.breakfast" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
              <el-collapse-item title="午餐" name="2">
                <div v-for="item in dietResult.content?.lunch" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
              <el-collapse-item title="晚餐" name="3">
                <div v-for="item in dietResult.content?.dinner" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
            </el-collapse>
            <div v-if="dietResult.content?.reason" style="margin-top: 12px; padding: 12px; background: #f5f7fa; border-radius: 4px">
              <strong>建议原因：</strong>{{ dietResult.content.reason }}
            </div>
          </div>
          <el-empty v-else description="点击按钮获取 AI 饮食推荐" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>运动推荐</span>
              <el-button type="primary" :loading="exerciseLoading" @click="getExerciseRecommend">获取推荐</el-button>
            </div>
          </template>
          <div v-if="exerciseResult">
            <div v-for="item in exerciseResult.content?.recommended_exercises" :key="item.name" style="padding: 8px 0; border-bottom: 1px solid #eee">
              <div style="font-weight: bold">{{ item.name }}</div>
              <div style="color: #666; font-size: 13px">{{ item.duration }} | {{ item.intensity }}</div>
              <div style="color: #999; font-size: 12px">{{ item.benefit }}</div>
            </div>
            <div v-if="exerciseResult.content?.precautions?.length" style="margin-top: 12px; padding: 12px; background: #fdf6ec; border-radius: 4px">
              <strong>注意事项：</strong>
              <div v-for="p in exerciseResult.content.precautions" :key="p" style="margin-top: 4px">{{ p }}</div>
            </div>
          </div>
          <el-empty v-else description="点击按钮获取 AI 运动推荐" />
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>历史推荐</template>
      <el-table :data="history" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="recommendation_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.recommendation_type === 'diet' ? 'success' : 'warning'">
              {{ row.recommendation_type === 'diet' ? '饮食' : '运动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="推荐详情" width="600px">
      <pre style="white-space: pre-wrap; font-size: 13px">{{ JSON.stringify(detailContent, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../../api/request'
import { ElMessage } from 'element-plus'

const dietLoading = ref(false)
const exerciseLoading = ref(false)
const dietResult = ref<any>(null)
const exerciseResult = ref<any>(null)
const history = ref<any[]>([])
const detailVisible = ref(false)
const detailContent = ref<any>(null)

async function getDietRecommend() {
  dietLoading.value = true
  try {
    dietResult.value = await request.post('/recommendations/diet')
    ElMessage.success('饮食推荐生成成功')
    await loadHistory()
  } finally {
    dietLoading.value = false
  }
}

async function getExerciseRecommend() {
  exerciseLoading.value = true
  try {
    exerciseResult.value = await request.post('/recommendations/exercise')
    ElMessage.success('运动推荐生成成功')
    await loadHistory()
  } finally {
    exerciseLoading.value = false
  }
}

async function loadHistory() {
  history.value = await request.get('/recommendations/history')
}

function showDetail(row: any) {
  detailContent.value = row.content
  detailVisible.value = true
}

onMounted(loadHistory)
</script>
```

---

### Task 21: 数据分析页面

**Files:**
- Create: `frontend/src/views/analytics/Analytics.vue`

- [ ] **Step 1: 编写数据分析 Analytics.vue**

```vue
<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>营养摄入趋势</template>
          <div ref="nutritionChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>热量收支平衡</template>
          <div ref="calorieChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>体重变化</template>
      <div style="text-align: center; padding: 40px; color: #999">
        当前体重：{{ currentWeight || '未设置' }} kg
        <div style="margin-top: 8px; font-size: 13px">定期更新体重以追踪变化趋势</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../api/request'

const nutritionChartRef = ref<HTMLElement>()
const calorieChartRef = ref<HTMLElement>()
const currentWeight = ref<number | null>(null)
let nutritionChart: echarts.ECharts | null = null
let calorieChart: echarts.ECharts | null = null

async function loadData() {
  try {
    const trend: any = await request.get('/analytics/nutrition-trend', { params: { days: 30 } })
    renderNutritionChart(trend)
    renderCalorieChart(trend)

    const weight: any = await request.get('/analytics/weight-trend')
    currentWeight.value = weight.current_weight
  } catch {}
}

function renderNutritionChart(data: any[]) {
  if (!nutritionChartRef.value) return
  nutritionChart = echarts.init(nutritionChartRef.value)
  nutritionChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['蛋白质(g)', '脂肪(g)', '碳水(g)'] },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', name: '克(g)' },
    series: [
      { name: '蛋白质(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.protein) },
      { name: '脂肪(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.fat) },
      { name: '碳水(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.carbs) },
    ],
  })
}

function renderCalorieChart(data: any[]) {
  if (!calorieChartRef.value) return
  calorieChart = echarts.init(calorieChartRef.value)
  calorieChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', name: 'kcal' },
    series: [
      {
        name: '每日热量',
        type: 'line',
        data: data.map(d => d.calories),
        markLine: { data: [{ yAxis: 2000, label: { formatter: '推荐2000kcal' } }] },
      },
    ],
  })
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    nutritionChart?.resize()
    calorieChart?.resize()
  })
})

onUnmounted(() => {
  nutritionChart?.dispose()
  calorieChart?.dispose()
})
</script>
```

---

### Task 22: App.vue 入口与全局样式

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/main.ts`

- [ ] **Step 1: 修改 App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 2: 修改 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

---

## 第四阶段：联调与收尾

### Task 23: 前后端联调测试

**Files:**
- None (manual testing)

- [ ] **Step 1: 启动后端**

```bash
cd backend
# 确保 MySQL 和 Redis 已启动
cp .env.example .env  # 编辑填入数据库密码等
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 2: 启动前端**

```bash
cd frontend
npm run dev
```

- [ ] **Step 3: 测试完整流程**

1. 访问 http://localhost:5173，应跳转到登录页
2. 点击"去注册"，注册一个新账号
3. 登录成功后进入仪表盘
4. 进入"健康档案"，填写身高体重、性别、病史等信息并保存
5. 进入"饮食记录"，选择今天日期，为早餐添加食物（搜索"米饭"）
6. 进入"AI 推荐"，点击"获取推荐"生成饮食方案
7. 进入"运动记录"，添加一条跑步记录
8. 进入"数据分析"，查看营养摄入图表
9. 返回仪表盘，确认数据汇总正确

- [ ] **Step 4: 提交代码**

```bash
git add .
git commit -m "feat: complete AI diet application with Vue 3 + FastAPI"
```

---

## 文件清单总览

### 后端文件
```
backend/
├── requirements.txt
├── .env.example
├── alembic.ini
├── alembic/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── ai_client.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── health_profile.py
│   │   ├── food.py
│   │   ├── daily_log.py
│   │   ├── exercise.py
│   │   └── recommendation.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── health.py
│   │   ├── food.py
│   │   ├── daily_log.py
│   │   ├── exercise.py
│   │   └── recommendation.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── health.py
│   │   ├── foods.py
│   │   ├── daily_logs.py
│   │   ├── exercise.py
│   │   ├── recommendations.py
│   │   └── analytics.py
│   └── seeds/
│       └── seed_foods.py
```

### 前端文件
```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── api/
│   │   └── request.ts
│   ├── router/
│   │   └── index.ts
│   ├── stores/
│   │   └── user.ts
│   ├── layouts/
│   │   └── MainLayout.vue
│   └── views/
│       ├── auth/
│       │   ├── Login.vue
│       │   └── Register.vue
│       ├── dashboard/
│       │   └── Dashboard.vue
│       ├── diet-log/
│       │   └── DietLog.vue
│       ├── health/
│       │   └── HealthProfile.vue
│       ├── exercise/
│       │   └── ExerciseLog.vue
│       ├── ai/
│       │   └── AIRecommend.vue
│       └── analytics/
│           └── Analytics.vue
```

## Self-Review

**Spec coverage:**
- 用户注册/登录 -> Task 5 (auth API) + Task 14 (前端登录注册)
- 用户信息管理 -> Task 6 + 前端健康档案页
- 健康档案(病史/过敏/生理期) -> Task 7 + Task 18
- 食物营养数据库搜索 -> Task 8 (含种子数据)
- 饮食日志 CRUD -> Task 9 + Task 17
- 运动记录 -> Task 10 + Task 19
- AI 饮食推荐 -> Task 11 + Task 20
- AI 运动推荐 -> Task 11 + Task 20
- 数据分析图表 -> Task 12 + Task 21
- 数据库迁移 -> Task 3
- JWT 认证 -> Task 4
- 全部覆盖，无遗漏。

**Placeholder scan:** 无 TBD/TODO，所有步骤含完整代码。

**Type consistency:** 所有模型字段名、Pydantic schema 属性、前端接口引用保持一致。
