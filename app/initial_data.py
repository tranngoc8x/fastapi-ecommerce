import logging

from sqlmodel import Session

from app.db.session import engine
from app.schemas.user import UserCreate
from app.services.business.user import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as db:
        user_service = UserService()
        
        # Check if admin user already exists
        admin_user = user_service.get_by_email(db, email="admin@example.com")
        if not admin_user:
            logger.info("Creating admin user")
            admin_in = UserCreate(
                email="admin@example.com",
                password="admin123",
                full_name="Admin User",
                is_admin=True,
            )
            user_service.create(db, user_in=admin_in)
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")


if __name__ == "__main__":
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")
