from app.services.business.user import UserService
from app.services.business.product import ProductService
from app.services.business.order import OrderService
from app.core.deps import user_service, product_service, order_service


def get_user_service() -> UserService:
    """Dependency for getting the user service."""
    return user_service


def get_product_service() -> ProductService:
    """Dependency for getting the product service."""
    return product_service


def get_order_service() -> OrderService:
    """Dependency for getting the order service."""
    return order_service
