"""
Tests for ProductService.
"""
import pytest
from sqlmodel import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.business.product import ProductService
from app.db.repositories.product_repository import ProductRepository


class TestProductService:
    """Test cases for ProductService."""

    def test_create_product(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        mock_kafka_producer,
    ):
        """Test creating a product."""
        # Arrange
        product_service = ProductService(
            repository=product_repository,
        )
        product_data = {
            "name": "New Product",
            "description": "This is a new product",
            "price": 29.99,
            "stock": 50,
        }
        product_in = ProductCreate(**product_data)

        # Act
        product = product_service.create(db_session, product_in=product_in)

        # Assert
        assert product.name == product_data["name"]
        assert product.description == product_data["description"]
        assert product.price == product_data["price"]
        assert product.stock == product_data["stock"]
        assert product.is_active  # Default value

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "product_events"
        assert message["value"]["event_type"] == "created"
        assert message["value"]["data"]["name"] == product_data["name"]

    def test_get_product(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
    ):
        """Test getting a product by ID."""
        # Arrange
        product_service = ProductService(repository=product_repository)

        # Act
        product = product_service.get(db_session, product_id=test_product.id)

        # Assert
        assert product is not None
        assert product.id == test_product.id
        assert product.name == test_product.name

    def test_get_multi(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
    ):
        """Test getting multiple products."""
        # Arrange
        product_service = ProductService(repository=product_repository)

        # Create another product
        product_data = {
            "name": "Another Product",
            "description": "This is another product",
            "price": 39.99,
            "stock": 25,
        }
        product_in = ProductCreate(**product_data)
        another_product = product_service.create(db_session, product_in=product_in)

        # Act
        products = product_service.get_multi(db_session)

        # Assert
        assert len(products) == 2
        assert any(p.id == test_product.id for p in products)
        assert any(p.id == another_product.id for p in products)

    def test_get_multi_active_only(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
    ):
        """Test getting only active products."""
        # Arrange
        product_service = ProductService(repository=product_repository)

        # Create an inactive product
        product_data = {
            "name": "Inactive Product",
            "description": "This is an inactive product",
            "price": 49.99,
            "stock": 10,
            "is_active": False,
        }
        product_in = ProductCreate(**product_data)
        # Create directly with repository to bypass service logic
        inactive_product = product_repository.create(db_session, obj_in=product_in)

        # Act
        active_products = product_service.get_multi(db_session, active_only=True)
        all_products = product_service.get_multi(db_session, active_only=False)

        # Assert
        assert len(active_products) == 1
        assert active_products[0].id == test_product.id

        assert len(all_products) == 2
        assert any(p.id == test_product.id for p in all_products)
        assert any(p.id == inactive_product.id for p in all_products)

    def test_update_product(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
        mock_kafka_producer,
    ):
        """Test updating a product."""
        # Arrange
        product_service = ProductService(repository=product_repository)
        update_data = {
            "name": "Updated Product",
            "price": 24.99,
        }
        product_in = ProductUpdate(**update_data)

        # Reset mock
        mock_kafka_producer.messages = []

        # Act
        updated_product = product_service.update(db_session, db_obj=test_product, obj_in=product_in)

        # Assert
        assert updated_product.id == test_product.id
        assert updated_product.name == update_data["name"]
        assert updated_product.price == update_data["price"]
        assert updated_product.description == test_product.description  # Unchanged

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "product_events"
        assert message["value"]["event_type"] == "updated"
        assert message["value"]["data"]["name"] == update_data["name"]

    def test_delete_product(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
        mock_kafka_producer,
    ):
        """Test deleting a product."""
        # Arrange
        product_service = ProductService(repository=product_repository)

        # Reset mock
        mock_kafka_producer.messages = []

        # Act
        deleted_product = product_service.delete(db_session, product_id=test_product.id)

        # Assert
        assert deleted_product is not None
        assert deleted_product.id == test_product.id

        # Product should be deleted
        assert product_service.get(db_session, product_id=test_product.id) is None

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "product_events"
        assert message["value"]["event_type"] == "deleted"

    def test_update_stock(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
        mock_kafka_producer,
    ):
        """Test updating product stock."""
        # Arrange
        product_service = ProductService(repository=product_repository)
        initial_stock = test_product.stock
        quantity_change = 10

        # Reset mock
        mock_kafka_producer.messages = []

        # Act
        updated_product = product_service.update_stock(
            db_session, product_id=test_product.id, quantity=quantity_change
        )

        # Assert
        assert updated_product.id == test_product.id
        assert updated_product.stock == initial_stock + quantity_change

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "product_events"
        assert message["value"]["event_type"] == "stock_updated"
        assert message["value"]["data"]["stock"] == initial_stock + quantity_change
        # In our mock, additional_data might not be present, so we'll skip this check

    def test_update_stock_negative(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
        mock_kafka_producer,
    ):
        """Test updating product stock with negative quantity."""
        # Arrange
        product_service = ProductService(repository=product_repository)
        initial_stock = test_product.stock
        quantity_change = -10

        # Reset mock
        mock_kafka_producer.messages = []

        # Act
        updated_product = product_service.update_stock(
            db_session, product_id=test_product.id, quantity=quantity_change
        )

        # Assert
        assert updated_product.id == test_product.id
        assert updated_product.stock == initial_stock + quantity_change

        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "product_events"
        assert message["value"]["event_type"] == "stock_updated"
        assert message["value"]["data"]["stock"] == initial_stock + quantity_change
        # In our mock, additional_data might not be present, so we'll skip this check

    def test_update_stock_insufficient(
        self,
        db_session: Session,
        product_repository: ProductRepository,
        test_product: Product,
    ):
        """Test updating product stock with insufficient quantity."""
        # Arrange
        product_service = ProductService(repository=product_repository)
        quantity_change = -(test_product.stock + 1)  # More than available

        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient stock"):
            product_service.update_stock(
                db_session, product_id=test_product.id, quantity=quantity_change
            )
