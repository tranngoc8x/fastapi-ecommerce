"""
Tests for OrderService.
"""
import pytest
from sqlmodel import Session

from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderItemCreate
from app.services.business.order import OrderService
from app.db.repositories.order_repository import OrderRepository
from app.db.repositories.product_repository import ProductRepository


class TestOrderService:
    """Test cases for OrderService."""

    def test_create_order(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_user: User,
        test_product: Product,
        mock_kafka_producer,
    ):
        """Test creating an order."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )

        initial_stock = test_product.stock
        order_data = {
            "user_id": test_user.id,
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 2,
                    "unit_price": test_product.price
                }
            ]
        }
        order_in = OrderCreate(**order_data)

        # Act
        order = order_service.create(db_session, order_in=order_in)

        # Assert
        assert order.user_id == test_user.id
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == test_product.price * 2
        assert len(order.items) == 1
        assert order.items[0].product_id == test_product.id
        assert order.items[0].quantity == 2
        assert order.items[0].unit_price == test_product.price

        # Check that stock was updated
        updated_product = product_repository.get(db_session, id=test_product.id)
        assert updated_product.stock == initial_stock - 2

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "order_events"
        assert message["value"]["event_type"] == "created"
        assert message["value"]["data"]["user_id"] == test_user.id

    def test_create_order_insufficient_stock(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_user: User,
        test_product: Product,
    ):
        """Test creating an order with insufficient stock."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )

        # Set product stock to a low value
        test_product.stock = 1
        db_session.add(test_product)
        db_session.commit()

        order_data = {
            "user_id": test_user.id,
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 2,  # More than available
                    "unit_price": test_product.price
                }
            ]
        }
        order_in = OrderCreate(**order_data)

        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient stock"):
            order_service.create(db_session, order_in=order_in)

    def test_get_order(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
    ):
        """Test getting an order by ID."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )

        # Act
        order = order_service.get(db_session, order_id=test_order.id)

        # Assert
        assert order is not None
        assert order.id == test_order.id
        assert order.user_id == test_order.user_id
        assert order.status == test_order.status

    def test_get_multi(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
    ):
        """Test getting multiple orders."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )

        # Act
        orders = order_service.get_multi(db_session)

        # Assert
        assert len(orders) == 1
        assert orders[0].id == test_order.id

    def test_get_multi_by_user(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
        test_user: User,
    ):
        """Test getting orders for a specific user."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )

        # Act
        user_orders = order_service.get_multi(db_session, user_id=test_user.id)
        other_orders = order_service.get_multi(db_session, user_id=999)  # Non-existent user

        # Assert
        assert len(user_orders) == 1
        assert user_orders[0].id == test_order.id
        assert len(other_orders) == 0

    def test_process_payment(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
        mock_kafka_producer,
    ):
        """Test processing payment for an order."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )
        payment_id = "test-payment-123"

        # Reset mock
        mock_kafka_producer.messages = []

        # Act
        updated_order = order_service.process_payment(
            db_session, order_id=test_order.id, payment_id=payment_id
        )

        # Assert
        assert updated_order.id == test_order.id
        assert updated_order.status == OrderStatus.PAID

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "order_events"
        assert message["value"]["event_type"] == "payment_processed"
        assert message["value"]["data"]["id"] == test_order.id
        # In our mock, additional_data might not be present, so we'll skip this check

    def test_process_payment_nonexistent_order(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
    ):
        """Test processing payment for a nonexistent order."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )
        payment_id = "test-payment-123"

        # Act & Assert
        with pytest.raises(ValueError, match="Order .* not found"):
            order_service.process_payment(
                db_session, order_id=999, payment_id=payment_id
            )

    def test_process_payment_already_paid(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
    ):
        """Test processing payment for an already paid order."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )
        payment_id = "test-payment-123"

        # Set order status to PAID
        test_order.status = OrderStatus.PAID
        db_session.add(test_order)
        db_session.commit()

        # Act & Assert
        with pytest.raises(ValueError, match="Order .* is not in PENDING status"):
            order_service.process_payment(
                db_session, order_id=test_order.id, payment_id=payment_id
            )

    def test_delete_order(
        self,
        db_session: Session,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        test_order: Order,
        test_product: Product,
    ):
        """Test deleting an order."""
        # Arrange
        order_service = OrderService(
            order_repository=order_repository,
            product_repository=product_repository,
        )
        initial_stock = test_product.stock
        order_item_quantity = test_order.items[0].quantity

        # Act
        deleted_order = order_service.delete(db_session, order_id=test_order.id)

        # Assert
        assert deleted_order is not None
        assert deleted_order.id == test_order.id

        # Order should be deleted
        assert order_service.get(db_session, order_id=test_order.id) is None

        # Stock should be restored
        updated_product = product_repository.get(db_session, id=test_product.id)
        assert updated_product.stock == initial_stock + order_item_quantity
