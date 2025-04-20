"""
Pytest configuration and fixtures.
"""
import os
from typing import Dict, Generator, Any

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.product_repository import ProductRepository
from app.db.repositories.order_repository import OrderRepository


# Use in-memory SQLite database for testing
@pytest.fixture(name="db_engine")
def db_engine_fixture():
    """Create a SQLAlchemy engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="db_session")
def db_session_fixture(db_engine) -> Generator[Session, None, None]:
    """Create a SQLAlchemy session for testing."""
    with Session(db_engine) as session:
        yield session


@pytest.fixture(name="user_repository")
def user_repository_fixture() -> UserRepository:
    """Create a user repository for testing."""
    return UserRepository()


@pytest.fixture(name="product_repository")
def product_repository_fixture() -> ProductRepository:
    """Create a product repository for testing."""
    return ProductRepository()


@pytest.fixture(name="order_repository")
def order_repository_fixture() -> OrderRepository:
    """Create an order repository for testing."""
    return OrderRepository()


@pytest.fixture(name="test_user")
def test_user_fixture(db_session: Session, user_repository: UserRepository) -> User:
    """Create a test user."""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
    }
    from app.schemas.user import UserCreate
    user_in = UserCreate(**user_data)
    return user_repository.create(db_session, obj_in=user_in)


@pytest.fixture(name="test_admin")
def test_admin_fixture(db_session: Session, user_repository: UserRepository) -> User:
    """Create a test admin user."""
    user_data = {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
    }
    from app.schemas.user import UserCreate
    user_in = UserCreate(**user_data)
    user = user_repository.create(db_session, obj_in=user_in)
    user.is_admin = True
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="test_product")
def test_product_fixture(db_session: Session, product_repository: ProductRepository) -> Product:
    """Create a test product."""
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 19.99,
        "stock": 100,
    }
    from app.schemas.product import ProductCreate
    product_in = ProductCreate(**product_data)
    return product_repository.create(db_session, obj_in=product_in)


@pytest.fixture(name="test_order")
def test_order_fixture(
    db_session: Session,
    order_repository: OrderRepository,
    test_user: User,
    test_product: Product,
) -> Order:
    """Create a test order."""
    # Create order
    order = Order(user_id=test_user.id, total_amount=test_product.price)
    
    # Create order item
    item = OrderItem(
        product_id=test_product.id,
        quantity=1,
        unit_price=test_product.price,
    )
    
    # Create order with items
    return order_repository.create_with_items(db_session, order=order, items=[item])


# Mock for Kafka producer
class MockKafkaProducer:
    """Mock Kafka producer for testing."""
    
    def __init__(self):
        self.messages = []
        self.topics = set()
    
    def send(self, topic_key: str, value: Any, key: str = None, **kwargs) -> bool:
        """Mock send method."""
        self.messages.append({
            "topic": topic_key,
            "value": value,
            "key": key,
        })
        self.topics.add(topic_key)
        return True
    
    def flush(self, timeout=None):
        """Mock flush method."""
        pass
    
    def close(self):
        """Mock close method."""
        pass


@pytest.fixture(name="mock_kafka_producer")
def mock_kafka_producer_fixture(monkeypatch):
    """Create a mock Kafka producer."""
    mock_producer = MockKafkaProducer()
    
    # Patch the BaseKafkaProducer class
    from app.services.infrastructure.kafka.producer import BaseKafkaProducer
    
    original_init = BaseKafkaProducer.__init__
    original_send = BaseKafkaProducer.send
    
    def mock_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._producer = mock_producer
    
    def mock_send(self, topic_key, value, key=None, **kwargs):
        return mock_producer.send(topic_key, value, key, **kwargs)
    
    monkeypatch.setattr(BaseKafkaProducer, "__init__", mock_init)
    monkeypatch.setattr(BaseKafkaProducer, "send", mock_send)
    
    return mock_producer


# Mock for Celery task
class MockCeleryTask:
    """Mock Celery task for testing."""
    
    def __init__(self):
        self.tasks = []
        self.task_id = "mock-task-id"
    
    def delay(self, *args, **kwargs):
        """Mock delay method."""
        self.tasks.append({
            "args": args,
            "kwargs": kwargs,
        })
        return self
    
    def apply_async(self, args=None, kwargs=None, **options):
        """Mock apply_async method."""
        self.tasks.append({
            "args": args or (),
            "kwargs": kwargs or {},
            "options": options,
        })
        return self


@pytest.fixture(name="mock_celery_task")
def mock_celery_task_fixture(monkeypatch):
    """Create a mock Celery task."""
    mock_task = MockCeleryTask()
    
    # Patch the import_products task
    from app.services.infrastructure.async_tasks.celery import tasks
    monkeypatch.setattr(tasks, "import_products", mock_task)
    
    return mock_task
