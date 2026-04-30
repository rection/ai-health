# AI 饮食应用设计文档

> 日期：2026-04-30
> 状态：已批准

## 1. 项目概述

AI 饮食应用是一个基于大模型的个性化健康管理 Web 应用。根据用户的个人档案（性别、身高体重、病史、生理期等）和历史饮食记录，通过 AI 生成个性化的饮食和运动建议，并支持每日饮食日志记录和数据分析。

## 2. 技术选型

| 层级 | 技术 | 用途 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API + `<script setup>`) | SPA 应用 |
| UI 组件库 | Element Plus | 表单、表格、卡片等 UI 组件 |
| 状态管理 | Pinia | 全局状态 |
| 路由 | Vue Router | 前端路由 |
| 图表 | ECharts | 数据可视化 |
| HTTP 客户端 | Axios | 前后端通信 |
| 后端框架 | FastAPI | RESTful API 服务 |
| 数据库 | MySQL | 持久化存储 |
| 缓存 | Redis | 会话、热门数据缓存 |
| 认证 | JWT + bcrypt | 用户认证和密码加密 |
| AI | Claude/OpenAI API | 智能饮食和运动推荐 |
| 营养数据 | 结构化数据库表 | 食物营养成分数据 |
| 部署 | 自托管服务器 | 个人/云服务器部署 |

## 3. 系统架构

```
┌─────────────────────────────────────────────────┐
│                  用户浏览器                        │
│              Vue 3 + Element Plus                 │
│          (Vue Router + Pinia + Axios)             │
└──────────────────────┬──────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼──────────────────────────┐
│              FastAPI 后端服务                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ 用户模块  │ │ 饮食模块  │ │ AI 推荐引擎      │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ 运动模块  │ │ 健康档案  │ │ 营养数据库服务    │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└──────┬──────────────┬───────────────┬───────────┘
       │              │               │
┌──────▼──────┐ ┌─────▼─────┐ ┌───────▼────────┐
│   MySQL     │ │   Redis   │ │ 大模型 API     │
│  (主数据库)  │ │ (缓存/会话)│ │ (Claude/GPT)  │
└─────────────┘ └───────────┘ └────────────────┘
```

## 4. 数据库设计

### 4.1 users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) UNIQUE NOT NULL | 用户名 |
| password_hash | VARCHAR(255) NOT NULL | 密码哈希 |
| email | VARCHAR(100) | 邮箱 |
| avatar | VARCHAR(500) | 头像 URL |
| gender | ENUM('male','female') | 性别 |
| birthday | DATE | 生日 |
| height_cm | DECIMAL(5,1) | 身高(cm) |
| weight_kg | DECIMAL(5,1) | 体重(kg) |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.2 health_profiles（健康档案表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| user_id | BIGINT FK UNIQUE | 关联用户 |
| allergies | JSON | 过敏信息 |
| diseases | JSON | 病史（糖尿病、高血压等） |
| dietary_preferences | JSON | 饮食偏好（素食、低碳水等） |
| menstrual_cycle_start | DATE | 生理期开始日期（女性） |
| menstrual_cycle_length | INT | 生理期周期天数（女性） |
| updated_at | DATETIME | 更新时间 |

### 4.3 food_database（食物营养数据库）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| name | VARCHAR(100) NOT NULL | 食物名称 |
| category | VARCHAR(50) | 分类（主食/肉类/蔬菜等） |
| calories_per_100g | DECIMAL(6,1) | 每100g热量(kcal) |
| protein_g | DECIMAL(5,1) | 蛋白质(g) |
| fat_g | DECIMAL(5,1) | 脂肪(g) |
| carbs_g | DECIMAL(5,1) | 碳水化合物(g) |
| fiber_g | DECIMAL(5,1) | 膳食纤维(g) |
| vitamins | JSON | 维生素数据 |
| minerals | JSON | 矿物质数据 |
| source | VARCHAR(50) | 数据来源 |

### 4.4 daily_logs（每日饮食日志）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| user_id | BIGINT FK | 关联用户 |
| date | DATE NOT NULL | 日期 |
| meal_type | ENUM('breakfast','lunch','dinner','snack') | 餐次 |
| created_at | DATETIME | 创建时间 |

### 4.5 log_items（日志明细）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| daily_log_id | BIGINT FK | 关联日志 |
| food_id | BIGINT FK NULLABLE | 关联食物库（自定义时为空） |
| quantity_g | DECIMAL(6,1) NOT NULL | 食用量(g) |
| custom_name | VARCHAR(100) | 自定义食物名称 |
| ai_nutrition | JSON | AI 估算的营养数据 |

### 4.6 exercise_logs（运动记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| user_id | BIGINT FK | 关联用户 |
| date | DATE NOT NULL | 日期 |
| exercise_type | VARCHAR(50) | 运动类型 |
| duration_min | INT | 时长(分钟) |
| calories_burned | DECIMAL(6,1) | 消耗热量(kcal) |

### 4.7 ai_recommendations（AI 推荐记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 主键 |
| user_id | BIGINT FK | 关联用户 |
| date | DATE NOT NULL | 日期 |
| recommendation_type | ENUM('diet','exercise') | 推荐类型 |
| content | JSON | AI 返回内容 |
| model_used | VARCHAR(50) | 使用的模型 |
| created_at | DATETIME | 创建时间 |

## 5. 前端页面结构

```
App
├── 登录/注册页
├── 主布局 (Layout)
│   ├── 侧边栏导航
│   ├── 仪表盘 (Dashboard)
│   │   ├── 今日营养概览卡片
│   │   ├── AI 今日推荐卡片
│   │   └── 本周饮食趋势图
│   ├── 饮食记录
│   │   ├── 今日记录 (按早/中/晚餐分组)
│   │   ├── 添加食物 (搜索食物库 + 自定义)
│   │   └── 历史记录 (日历视图)
│   ├── AI 推荐中心
│   │   ├── 今日饮食方案
│   │   ├── 运动建议
│   │   └── 周期分析报告
│   ├── 健康档案
│   │   ├── 基本信息 (身高/体重/生日)
│   │   ├── 病史管理
│   │   ├── 过敏与偏好
│   │   └── 生理期记录 (女性)
│   ├── 运动记录
│   │   ├── 今日运动
│   │   └── AI 运动推荐
│   └── 数据分析
│       ├── 营养摄入趋势 (图表)
│       ├── 体重变化曲线
│       └── 热量收支平衡
```

## 6. 后端 API 设计

| 模块 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 认证 | POST | /api/auth/register | 用户注册 |
| 认证 | POST | /api/auth/login | 登录，返回 JWT |
| 用户 | GET | /api/users/me | 获取个人信息 |
| 用户 | PUT | /api/users/me | 更新个人信息 |
| 健康档案 | GET | /api/health-profile | 获取健康档案 |
| 健康档案 | PUT | /api/health-profile | 更新健康档案 |
| 食物库 | GET | /api/foods/search?q= | 搜索食物及营养数据 |
| 饮食日志 | GET | /api/daily-logs | 获取日志列表 |
| 饮食日志 | POST | /api/daily-logs | 创建日志 |
| 饮食日志 | POST | /api/daily-logs/{id}/items | 添加食物条目 |
| 饮食日志 | DELETE | /api/daily-logs/{id}/items/{item_id} | 删除食物条目 |
| AI 推荐 | POST | /api/recommendations/diet | 生成饮食推荐 |
| AI 推荐 | POST | /api/recommendations/exercise | 生成运动推荐 |
| AI 推荐 | GET | /api/recommendations/history | 历史推荐记录 |
| 运动 | GET | /api/exercise-logs | 获取运动记录 |
| 运动 | POST | /api/exercise-logs | 添加运动记录 |
| 数据分析 | GET | /api/analytics/nutrition-trend | 营养趋势数据 |
| 数据分析 | GET | /api/analytics/weight-trend | 体重趋势数据 |

## 7. AI 推荐引擎

### 7.1 推荐流程

```
用户请求推荐
  → 收集用户档案 (性别/身高/体重/病史/生理期)
  → 拉取近7天饮食记录
  → 检查营养数据库缺口
  → 构造 Prompt 发送给大模型 API
  → 解析返回结果 → 存储并返回给用户
```

### 7.2 饮食推荐 Prompt 模板

```
你是一位专业的营养师。请根据以下用户信息生成今日饮食方案：

【用户信息】
- 性别：{gender}
- 年龄：{age}
- 身高：{height_cm}cm，体重：{weight_kg}kg，BMI：{bmi}
- 病史：{diseases}
- 过敏：{allergies}
- 饮食偏好：{preferences}
- 当前生理期状态：{menstrual_status}（如适用）

【近7天饮食分析】
{nutrition_summary}

请输出：
1. 今日三餐具体菜品建议（含分量）
2. 需要补充的营养素
3. 需要避免的食物
4. 简要原因说明
```

### 7.3 运动推荐 Prompt 模板

```
你是一位专业的运动康复师。请根据以下用户信息生成运动建议：

【用户信息】
- 性别：{gender}
- 年龄：{age}
- BMI：{bmi}
- 病史：{diseases}
- 近期运动频率：{recent_exercise_summary}
- 当前生理期状态：{menstrual_status}（如适用）

请输出：
1. 今日推荐运动项目（含时长和强度）
2. 需要避免的运动
3. 注意事项
```

## 8. 目录结构

```
ai-diet/
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # 公共组件
│   │   ├── layouts/          # 布局组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── views/            # 页面视图
│   │   │   ├── auth/         # 登录/注册
│   │   │   ├── dashboard/    # 仪表盘
│   │   │   ├── diet-log/     # 饮食记录
│   │   │   ├── health/       # 健康档案
│   │   │   ├── exercise/     # 运动记录
│   │   │   ├── ai/           # AI 推荐
│   │   │   └── analytics/    # 数据分析
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── health.py
│   │   │   ├── foods.py
│   │   │   ├── daily_logs.py
│   │   │   ├── exercise.py
│   │   │   ├── recommendations.py
│   │   │   └── analytics.py
│   │   ├── core/             # 核心配置
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── ai_client.py
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   └── main.py
│   ├── requirements.txt
│   └── alembic/              # 数据库迁移
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-30-ai-diet-app-design.md
```

## 9. 安全与约束

- 密码使用 bcrypt 哈希存储
- JWT Token 有效期 24 小时，支持刷新
- API 请求频率限制（防止 AI 接口被滥用）
- 用户只能访问自己的数据（基于 user_id 的权限隔离）
- AI 调用设置超时（15秒）和重试机制
- 敏感数据（病史、健康信息）加密存储
