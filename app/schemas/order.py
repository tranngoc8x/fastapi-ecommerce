from datetime import datetime
from typing import List, Optional, ForwardRef

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


# Forward reference for User
UserRef = ForwardRef('User')


class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    """Order item creation schema."""
    pass


class OrderItemUpdate(BaseModel):
    """Order item update schema."""
    quantity: Optional[int] = Field(None, gt=0)


class OrderItemInDBBase(OrderItemBase):
    """Order item in DB base schema."""
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDBBase):
    """Order item schema for API responses."""
    pass


class OrderBase(BaseModel):
    """Base order schema."""
    user_id: int
    status: OrderStatus = OrderStatus.PENDING
    payment_id: Optional[str] = None


class OrderCreate(BaseModel):
    """Order creation schema."""
    user_id: int
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Order update schema."""
    status: Optional[OrderStatus] = None
    payment_id: Optional[str] = None


class OrderInDBBase(OrderBase):
    """Order in DB base schema."""
    id: int
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    """Order schema for API responses."""
    items: List[OrderItem]


class OrderWithUser(Order):
    """Order schema with user information."""
    user: UserRef


# Import User after defining OrderWithUser to avoid circular imports
from app.schemas.user import User
OrderWithUser.update_forward_refs()
