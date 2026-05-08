from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .database import get_session,engine, Base
from .models import Category, Item, Sell
from .shemas import CategorySchema, ItemSchema, SellSchema, SellOutSchema, ItemOutSchema

router = APIRouter()

@router.post("/items/")
async def create_item(
    item: ItemSchema,
    db: AsyncSession = Depends(get_session),
    ):
    
    new_item = Item(
        name=item.name,
        price=item.price,
        quantity=item.quantity,
        category_id=item.category_id
        )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.get("/items/")
async def read_items(
    category_id: int | None = None,
    db: AsyncSession = Depends(get_session),
    ) -> list[ItemOutSchema]:
    if category_id is not None:
        result = await db.execute(
            select(Item).where(Item.category_id == category_id)
        )
    else:
        result = await db.execute(select(Item))
    items = result.scalars().all()
    return [
        ItemOutSchema(
            id=item.id,
            name=item.name,
            price=item.price,
            quantity=item.quantity,
            category_id=item.category_id
        )
        for item in items
    ]

@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: ItemSchema,
    db: AsyncSession = Depends(get_session),
    ):
    result = await db.execute(select(Item).where(Item.id == item_id))
    existing_item = result.scalar_one_or_none()
    if existing_item is None:
        raise HTTPException(404, "Item not found")
    
    existing_item.name = item.name
    existing_item.price = item.price
    existing_item.quantity = item.quantity
    existing_item.category_id = item.category_id
    
    await db.commit()
    await db.refresh(existing_item)
    return existing_item

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_session),
    ):
    result = await db.execute(select(Item).where(Item.id == item_id))
    existing_item = result.scalar_one_or_none()
    if existing_item is None:
        raise HTTPException(404, "Item not found")
    
    await db.delete(existing_item)
    await db.commit()
    return {"message": "Item deleted successfully"}

@router.post("/sells/")
async def create_sell(
    sell: SellSchema,
    db: AsyncSession =Depends(get_session),
    )-> SellOutSchema:
    result = await db.execute(select(Item).where(Item.id == sell.item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(404, "Item not found")
    if item.quantity < sell.quantity_sold:
        raise HTTPException(400, "Not enough quantity in stock")
    item.quantity -= sell.quantity_sold
    total_price = item.price * sell.quantity_sold
    sale_date = sell.created_at if sell.created_at else datetime.now()
    new_sell = Sell(
        item_id=sell.item_id,
        quantity_sold=sell.quantity_sold,
        total_price=total_price,
        created_at=str(sale_date)
    )
    db.add(new_sell)
    await db.commit()
    await db.refresh(new_sell)
    return SellOutSchema(
        id=new_sell.id,
        item_id=new_sell.item_id,
        quantity_sold=new_sell.quantity_sold,
        total_price=new_sell.total_price,
        created_at=new_sell.created_at
    )

@router.get("/sells/")
async def read_sells(
    db: AsyncSession = Depends(get_session),
    ) -> list[SellOutSchema]:
    result = await db.execute(select(Sell))
    sells = result.scalars().all()
    return [
        SellOutSchema(
            id=sell.id,
            item_id=sell.item_id,
            quantity_sold=sell.quantity_sold,
            total_price=sell.total_price,
            created_at=sell.created_at
        )
        for sell in sells
    ]

@router.post("/categories/")
async def create_category(
    category: CategorySchema,
    db: AsyncSession = Depends(get_session),
    ):
    new_category = Category(
        name=category.name
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

@router.get("/analytics/revenue/")
async def get_revenue(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: AsyncSession = Depends(get_session),
    ) -> tuple[list[SellOutSchema], float]:
    
    query = select(Sell)
    if from_date is not None:
        query = query.where(Sell.created_at >= str(from_date))
    
    if to_date is not None:
        query = query.where(Sell.created_at <= str(to_date))
    
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(400, "from_date cannot be greater than to_date")
    
    if from_date is not None and to_date is not None:
        query = query.where(Sell.created_at.between(str(from_date), str(to_date)))
        
    result = await db.execute(query)
    sells = result.scalars().all()
    total_revenue = sum(sell.total_price for sell in sells)
    
    return [
        SellOutSchema(
            id=sell.id,
            item_id=sell.item_id,
            quantity_sold=sell.quantity_sold,
            total_price=sell.total_price,
            created_at=sell.created_at
        )
        for sell in sells
    ], total_revenue


@router.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"message": "Database setup completed"}