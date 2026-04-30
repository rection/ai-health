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
