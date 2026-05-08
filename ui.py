import streamlit as st
import requests
import pandas as pd
from datetime import datetime

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)
# Настройки подключения
# Если запускаешь ВНЕ докера, используй localhost:8090
# Если внутри докера в той же сети, используй app:8080
BASE_URL = "http://localhost:8090" 

st.set_page_config(page_title="Shop Admin Panel", layout="wide")

st.title("📦 Система управления магазином")

tabs = st.tabs(["📊 Аналитика", "🛒 Продажи", "📦 Склад", "📁 Категории"])

# --- ВКЛАДКА АНАЛИТИКИ ---
with tabs[0]:
    st.header("Аналитика выручки")
    
    col1, col2 = st.columns(2)
    with col1:
        from_d = st.date_input("С", value=datetime(2026, 1, 1))
    with col2:
        to_d = st.date_input("По", value=datetime.now())

    if st.button("Рассчитать выручку"):
        # Формируем параметры для FastAPI (он ждет ISO строку)
        params = {
            "from_date": from_d.isoformat(),
            "to_date": to_d.isoformat()
        }
        res = requests.get(f"{BASE_URL}/analytics/revenue/", params=params)
        
        if res.status_code == 200:
            sells_data, total_revenue = res.json()
            
            st.metric("Общая выручка за период", f"{total_revenue:.2f} руб.")
            
            if sells_data:
                df_sells = pd.DataFrame(sells_data)
                st.subheader("Лог транзакций")
                st.dataframe(df_sells, use_container_width=True)
                
                df_sells['created_at'] = pd.to_datetime(df_sells['created_at'])
                chart_data = df_sells.groupby(df_sells['created_at'].dt.date)['total_price'].sum()
                st.line_chart(chart_data)
            else:
                st.info("За этот период продаж не найдено.")
        else:
            st.error("Ошибка при получении аналитики")

# --- ВКЛАДКА ПРОДАЖ ---
with tabs[1]:
    st.header("Оформление новой продажи")
    
    with st.form("sell_form"):
        item_id = st.number_input("ID товара", min_value=1, step=1)
        
        quantity = st.number_input("Количество к продаже", min_value=1, step=1)
        
        sale_date = st.date_input("Дата совершения продажи", value=datetime.now())
        
        submit_sell = st.form_submit_button("Продать")
        
        if submit_sell:
            payload = {"item_id": item_id, "quantity_sold": quantity}
            res = requests.post(f"{BASE_URL}/sells/", json=payload)
            if res.status_code == 200:
                data = res.json()
                st.success(f"Продажа оформлена! Итог: {data['total_price']} руб.")
            else:
                st.error(f"Ошибка: {res.json().get('detail', 'Неизвестная ошибка')}")

# --- ВКЛАДКА СКЛАДА ---
with tabs[2]:
    st.header("Управление товарами")
    
    # Список товаров
    st.subheader("Текущие остатки")
    if st.button("Обновить список товаров"):
        res = requests.get(f"{BASE_URL}/items/")
        if res.status_code == 200:
            items_df = pd.DataFrame(res.json())
            st.dataframe(items_df, use_container_width=True)

    st.divider()
    
    # Добавление товара
    st.subheader("Добавить новый товар")
    with st.expander("Форма добавления"):
        with st.form("add_item_form"):
            name = st.text_input("Название")
            price = st.number_input("Цена", min_value=0.0, format="%.2f")
            qty = st.number_input("Количество", min_value=0, step=1)
            cat_id = st.number_input("ID категории", min_value=1, step=1)
            
            if st.form_submit_button("Создать"):
                payload = {"name": name, "price": price, "quantity": qty, "category_id": cat_id}
                res = requests.post(f"{BASE_URL}/items/", json=payload)
                if res.status_code == 200:
                    st.success("Товар успешно добавлен!")
                else:
                    st.error("Ошибка при добавлении")

# --- ВКЛАДКА КАТЕГОРИЙ ---
with tabs[3]:
    st.header("Категории")
    with st.form("cat_form"):
        cat_name = st.text_input("Название новой категории")
        if st.form_submit_button("Создать категорию"):
            res = requests.post(f"{BASE_URL}/categories/", json={"name": cat_name})
            if res.status_code == 200:
                st.success(f"Категория '{cat_name}' создана")
            else:
                st.error("Ошибка")

    if st.button("Инициализировать БД (Setup)"):
        res = requests.post(f"{BASE_URL}/setup_database")
        st.write(res.json())