from typing import List, Optional

from sqlmodel import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.messaging_service import EventType, MessagingService


class UserService:
    """Service for user operations."""

    def __init__(self,
                 repository: UserRepository = UserRepository(),
                 messaging_service: MessagingService = MessagingService()):
        self.repository = repository
        self.messaging_service = messaging_service

    def create(self, db: Session, *, user_in: UserCreate) -> User:
        """Create a new user."""
        user = self.repository.create(db, obj_in=user_in)

        # Send message to Kafka
        self.messaging_service.send_user_event(
            user=user,
            event_type=EventType.CREATED
        )

        return user

    def get(self, db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.repository.get(db, id=user_id)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.repository.get_by_email(db, email=email)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users."""
        return self.repository.get_multi(db, skip=skip, limit=limit)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update a user."""
        updated_user = self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

        # Send message to Kafka
        self.messaging_service.send_user_event(
            user=updated_user,
            event_type=EventType.UPDATED
        )

        return updated_user

    def delete(self, db: Session, *, user_id: int) -> Optional[User]:
        """Delete a user."""
        user = self.repository.get(db, id=user_id)
        if user:
            # Send message to Kafka before deleting
            self.messaging_service.send_user_event(
                user=user,
                event_type=EventType.DELETED
            )

            return self.repository.remove(db, id=user_id)
        return None

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        return self.repository.authenticate(db, email=email, password=password)
