from typing import List, Optional

from sqlmodel import Session

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.db.repositories.order_repository import OrderRepository
from app.db.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate
from app.services.infrastructure.messaging.service import EventType, MessagingService


class OrderService:
    """Service for order operations."""

    def __init__(
        self,
        order_repository: OrderRepository = OrderRepository(),
        product_repository: ProductRepository = ProductRepository(),
        messaging_service: MessagingService = MessagingService()
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.messaging_service = messaging_service

    def create(self, db: Session, *, order_in: OrderCreate) -> Order:
        """Create a new order."""
        # Create order
        order = Order(user_id=order_in.user_id)

        # Create order items and calculate total
        total_amount = 0.0
        items = []

        for item_in in order_in.items:
            # Get product to verify price and stock
            product = self.product_repository.get(db, id=item_in.product_id)
            if not product or not product.is_active:
                raise ValueError(f"Product {item_in.product_id} not found or inactive")

            if product.stock < item_in.quantity:
                raise ValueError(f"Insufficient stock for product {product.id}")

            # Create order item
            order_item = OrderItem(
                product_id=product.id,
                quantity=item_in.quantity,
                unit_price=product.price
            )
            items.append(order_item)

            # Update product stock
            self.product_repository.update_stock(db, product_id=product.id, quantity=-item_in.quantity)

            # Add to total
            total_amount += product.price * item_in.quantity

        # Update order total
        order.total_amount = total_amount

        # Create order with items
        created_order = self.order_repository.create_with_items(db, order=order, items=items)

        # Send message to Kafka
        self.messaging_service.send_order_event(
            order=created_order,
            event_type=EventType.CREATED
        )

        return created_order

    def get(self, db: Session, order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        return self.order_repository.get(db, id=order_id)

    def get_multi(
        self, db: Session, *, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get multiple orders."""
        if user_id:
            return self.order_repository.get_multi_by_user(db, user_id=user_id, skip=skip, limit=limit)
        else:
            return self.order_repository.get_multi(db, skip=skip, limit=limit)

    def update(self, db: Session, *, db_obj: Order, obj_in: OrderUpdate) -> Order:
        """Update an order."""
        return self.order_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, order_id: int) -> Optional[Order]:
        """Delete an order."""
        order = self.order_repository.get(db, id=order_id)
        if order:
            # Restore product stock for each order item
            for item in order.items:
                self.product_repository.update_stock(db, product_id=item.product_id, quantity=item.quantity)

            # Delete order
            return self.order_repository.remove(db, id=order_id)
        return None

    def process_payment(self, db: Session, *, order_id: int, payment_id: str) -> Order:
        """Process payment for an order."""
        order = self.order_repository.get(db, id=order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order {order_id} is not in PENDING status")

        # Update order status
        updated_order = self.order_repository.update_status(db, order_id=order_id, status=OrderStatus.PAID)

        # Send message to Kafka
        self.messaging_service.send_order_event(
            order=updated_order,
            event_type=EventType.PAYMENT_PROCESSED,
            additional_data={"payment_id": payment_id}
        )

        return updated_order
