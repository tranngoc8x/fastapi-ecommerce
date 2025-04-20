"""
API dependencies package.
"""

from app.api.dependencies.auth import get_current_active_user, get_current_admin_user
from app.api.dependencies.database import get_db
from app.api.dependencies.services import get_user_service, get_product_service, get_order_service
