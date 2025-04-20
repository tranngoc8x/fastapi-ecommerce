from typing import List, Optional

from sqlmodel import Session

from app.models.product import Product
from app.db.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.infrastructure.messaging.service import EventType, MessagingService


class ProductService:
    """Service for product operations."""

    def __init__(self,
                 repository: ProductRepository = ProductRepository(),
                 messaging_service: MessagingService = MessagingService()):
        self.repository = repository
        self.messaging_service = messaging_service

    def create(self, db: Session, *, product_in: ProductCreate) -> Product:
        """Create a new product."""
        product = self.repository.create(db, obj_in=product_in)

        # Send message to Kafka
        self.messaging_service.send_product_event(
            product=product,
            event_type=EventType.CREATED
        )

        return product

    def get(self, db: Session, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        return self.repository.get(db, id=product_id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Product]:
        """Get multiple products."""
        return self.repository.get_multi(db, skip=skip, limit=limit, active_only=active_only)

    def update(self, db: Session, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        """Update a product."""
        updated_product = self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

        # Send message to Kafka
        self.messaging_service.send_product_event(
            product=updated_product,
            event_type=EventType.UPDATED
        )

        return updated_product

    def delete(self, db: Session, *, product_id: int) -> Optional[Product]:
        """Delete a product."""
        product = self.repository.get(db, id=product_id)
        if product:
            # Send message to Kafka before deleting
            self.messaging_service.send_product_event(
                product=product,
                event_type=EventType.DELETED
            )

            return self.repository.remove(db, id=product_id)
        return None

    def update_stock(self, db: Session, *, product_id: int, quantity: int) -> Product:
        """Update product stock."""
        updated_product = self.repository.update_stock(db, product_id=product_id, quantity=quantity)

        # Send message to Kafka
        self.messaging_service.send_product_event(
            product=updated_product,
            event_type=EventType.STOCK_UPDATED,
            additional_data={"quantity_change": quantity}
        )

        return updated_product
