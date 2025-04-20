from typing import Any, List, Optional

from sqlmodel import Session, select

from app.models.order import Order, OrderItem, OrderStatus
from app.db.repositories.base_repository import BaseRepository
from app.schemas.order import OrderCreate, OrderUpdate


class OrderRepository(BaseRepository[Order, OrderCreate, OrderUpdate]):
    """Repository for order operations."""

    def __init__(self):
        super().__init__(Order)

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get multiple orders for a specific user.

        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        statement = select(Order).where(Order.user_id == user_id).offset(skip).limit(limit)
        return db.exec(statement).all()

    def create_with_items(
        self, db: Session, *, order: Order, items: List[OrderItem]
    ) -> Order:
        """
        Create an order with its items.

        Args:
            db: Database session
            order: Order to create
            items: Order items to create

        Returns:
            Created order
        """
        db.add(order)
        db.flush()  # Get order ID without committing

        # Add items to order
        for item in items:
            item.order_id = order.id
            db.add(item)

        db.commit()
        db.refresh(order)
        return order

    def update_status(
        self, db: Session, *, order_id: int, status: OrderStatus
    ) -> Optional[Order]:
        """
        Update order status.

        Args:
            db: Database session
            order_id: ID of the order to update
            status: New status

        Returns:
            Updated order if found, None otherwise
        """
        order = self.get(db, order_id)
        if not order:
            return None

        order.status = status
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_order_items(self, db: Session, *, order_id: int) -> List[OrderItem]:
        """
        Get items for a specific order.

        Args:
            db: Database session
            order_id: ID of the order

        Returns:
            List of order items
        """
        statement = select(OrderItem).where(OrderItem.order_id == order_id)
        return db.exec(statement).all()

    def remove(self, db: Session, *, id: Any) -> Optional[Order]:
        """
        Remove an order and its items.

        Args:
            db: Database session
            id: ID of the order to remove

        Returns:
            Removed order if found, None otherwise
        """
        order = self.get(db, id)
        if order:
            # First delete all order items
            items = self.get_order_items(db, order_id=id)
            for item in items:
                db.delete(item)

            # Then delete the order
            db.delete(order)
            db.commit()
        return order
