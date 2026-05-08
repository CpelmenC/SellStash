from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session
from fastapi import Depends, HTTPException
from .models import Item, Sell
from .shemas import ItemSchema, SellSchema, SellOutSchema, ItemOutSchema

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
    new_sell = Sell(
        item_id=sell.item_id,
        quantity_sold=sell.quantity_sold,
        total_price=total_price,
        created_at=str(datetime.now())
    )
    db.add(new_sell)
    await db.commit()
    await db.refresh(new_sell)
    return SellOutSchema(
        id=new_sell.id,
        item_id=new_sell.item_id,
        quantity_sold=new_sell.quantity_sold,
        total_price=new_sell.total_price
    )