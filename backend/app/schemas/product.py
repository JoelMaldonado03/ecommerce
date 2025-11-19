from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_filename: Optional[str] = None

class ProductUpdate(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_filename: Optional[str] = None

class ProductSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_filename: Optional[str] = None
    created_at: Optional[datetime]

    class Config:
        from_attributes = True  # o orm_mode = True si prefieres compatibilidad clásica
