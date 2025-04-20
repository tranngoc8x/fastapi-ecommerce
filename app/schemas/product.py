from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[HttpUrl] = None


class ProductCreate(ProductBase):
    """Product creation schema."""
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class ProductInDBBase(ProductBase):
    """Product in DB base schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Product(ProductInDBBase):
    """Product schema for API responses."""
    pass
