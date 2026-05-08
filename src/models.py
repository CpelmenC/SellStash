from sqlalchemy.orm import Mapped, mapped_column,relationship   
from .database import Base

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[int]
    category_id: Mapped[int]

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class Sell(Base):
    __tablename__ = "sells"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int]
    quantity_sold: Mapped[int]
    total_price: Mapped[float]
    created_at: Mapped[str]

class ItemCategory(Base):
    __tablename__ = "item_category"
    item_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(primary_key=True)

