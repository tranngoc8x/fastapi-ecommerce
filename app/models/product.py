from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Product(SQLModel, table=True):
    """Product database model."""
    
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="product")
