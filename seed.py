import requests
import random
from datetime import datetime, timedelta

# Настройки — проверь порт, если менял в docker-compose
BASE_URL = "http://localhost:8090"

def seed_database():
    print("🚀 Начинаю наполнение базы данных...")

    # 1. Создаем категорию
    try:
        cat_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Продукты"})
        cat_res.raise_for_status()
        category = cat_res.json()
        cat_id = category["id"]
        print(f"✅ Категория создана: {category['name']} (ID: {cat_id})")
    except Exception as e:
        print(f"❌ Ошибка при создании категории: {e}")
        return

    # 2. Создаем товары
    items_to_create = [
        {"name": "Молоко", "price": 90.0, "quantity": 50, "category_id": cat_id},
        {"name": "Хлеб", "price": 45.0, "quantity": 100, "category_id": cat_id},
        {"name": "Сыр", "price": 750.0, "quantity": 20, "category_id": cat_id},
        {"name": "Яблоки", "price": 120.0, "quantity": 60, "category_id": cat_id}
    ]

    item_ids = []
    for item_data in items_to_create:
        res = requests.post(f"{BASE_URL}/items/", json=item_data)
        if res.status_code == 200:
            new_item = res.json()
            item_ids.append(new_item["id"])
            print(f"📦 Добавлен товар: {new_item['name']} (Цена: {new_item['price']})")

    # 3. Генерируем продажи за последние 7 дней
    print("📈 Генерирую продажи для аналитики...")
    
    # Список для имитации разной активности по дням
    sales_count = 0
    
    for day_offset in range(7, -1, -1):  # От 7 дней назад до сегодня
        # Определяем дату
        target_date = datetime.now() - timedelta(days=day_offset)
        
        # Количество продаж в этот день (от 2 до 6)
        daily_sales_limit = random.randint(2, 6)
        
        for _ in range(daily_sales_limit):
            # Выбираем случайный товар из созданных
            item_id = random.choice(item_ids)
            qty = random.randint(1, 4)
            
            payload = {
                "item_id": item_id,
                "quantity_sold": qty,
                "created_at": target_date.isoformat() # Тот самый ввод даты
            }
            
            res = requests.post(f"{BASE_URL}/sells/", json=payload)
            if res.status_code == 200:
                sales_count += 1
            else:
                # Если товар закончился (quantity стал 0), просто пропускаем
                pass

    print(f"🏁 Готово! Создано категорий: 1, товаров: {len(item_ids)}, продаж: {sales_count}.")
    print("🔗 Теперь открывай Streamlit и смотри вкладку 'Аналитика'.")

if __name__ == "__main__":
    seed_database()