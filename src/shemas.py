from pydantic import BaseModel

class ItemSchema(BaseModel):
    name:str
    price:float
    quantity:int
    category_id:int

class ItemUpdateSchema(BaseModel):
    name:str|None = None
    price:float|None = None
    quantity:int|None = None
    category_id:int|None = None

class ItemOutSchema(BaseModel):
    id:int
    name:str
    price:float
    quantity:int
    category_id:int

class CategorySchema(BaseModel):
    name:str

class SellSchema(BaseModel):
    item_id:int
    quantity_sold:int

class SellOutSchema(BaseModel):
    id:int
    item_id:int
    quantity_sold:int
    total_price:float
    created_at:str