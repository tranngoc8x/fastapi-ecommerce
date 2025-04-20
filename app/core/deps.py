"""
Global dependencies and instances for the application.
This module contains global instances of repositories and services
to avoid recreating them for each request.
"""

from app.db.repositories.user_repository import UserRepository
from app.db.repositories.product_repository import ProductRepository
from app.db.repositories.order_repository import OrderRepository
from app.services.business.user import UserService
from app.services.business.product import ProductService
from app.services.business.order import OrderService
from app.services.infrastructure.messaging.service import MessagingService
from app.services.infrastructure.messaging.kafka.client import kafka_client

# Global repository instances
user_repository = UserRepository()
product_repository = ProductRepository()
order_repository = OrderRepository()

# Global messaging service
messaging_service = MessagingService()

# Global service instances
user_service = UserService(repository=user_repository, messaging_service=messaging_service)
product_service = ProductService(repository=product_repository, messaging_service=messaging_service)
order_service = OrderService(
    order_repository=order_repository,
    product_repository=product_repository,
    messaging_service=messaging_service
)
