"""
Tests for UserService.
"""
import pytest
from sqlmodel import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.business.user import UserService
from app.db.repositories.user_repository import UserRepository


class TestUserService:
    """Test cases for UserService."""
    
    def test_create_user(
        self,
        db_session: Session,
        user_repository: UserRepository,
        mock_kafka_producer,
    ):
        """Test creating a user."""
        # Arrange
        user_service = UserService(
            repository=user_repository,
        )
        user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        }
        user_in = UserCreate(**user_data)
        
        # Act
        user = user_service.create(db_session, user_in=user_in)
        
        # Assert
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.verify_password(user_data["password"])
        assert not user.is_admin
        assert user.is_active
        
        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "user_events"
        assert message["value"]["event_type"] == "created"
        assert message["value"]["data"]["email"] == user_data["email"]
    
    def test_get_user(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
    ):
        """Test getting a user by ID."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        user = user_service.get(db_session, user_id=test_user.id)
        
        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_email(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
    ):
        """Test getting a user by email."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        user = user_service.get_by_email(db_session, email=test_user.email)
        
        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_multi(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
        test_admin: User,
    ):
        """Test getting multiple users."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        users = user_service.get_multi(db_session)
        
        # Assert
        assert len(users) == 2
        assert any(u.id == test_user.id for u in users)
        assert any(u.id == test_admin.id for u in users)
    
    def test_update_user(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
        mock_kafka_producer,
    ):
        """Test updating a user."""
        # Arrange
        user_service = UserService(repository=user_repository)
        update_data = {
            "full_name": "Updated User",
        }
        user_in = UserUpdate(**update_data)
        
        # Reset mock
        mock_kafka_producer.messages = []
        
        # Act
        updated_user = user_service.update(db_session, db_obj=test_user, obj_in=user_in)
        
        # Assert
        assert updated_user.id == test_user.id
        assert updated_user.full_name == update_data["full_name"]
        assert updated_user.email == test_user.email  # Unchanged
        
        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "user_events"
        assert message["value"]["event_type"] == "updated"
        assert message["value"]["data"]["full_name"] == update_data["full_name"]
    
    def test_update_user_password(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
    ):
        """Test updating a user's password."""
        # Arrange
        user_service = UserService(repository=user_repository)
        new_password = "newpassword123"
        update_data = {
            "password": new_password,
        }
        user_in = UserUpdate(**update_data)
        
        # Act
        updated_user = user_service.update(db_session, db_obj=test_user, obj_in=user_in)
        
        # Assert
        assert updated_user.id == test_user.id
        assert updated_user.verify_password(new_password)
    
    def test_delete_user(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
        mock_kafka_producer,
    ):
        """Test deleting a user."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Reset mock
        mock_kafka_producer.messages = []
        
        # Act
        deleted_user = user_service.delete(db_session, user_id=test_user.id)
        
        # Assert
        assert deleted_user is not None
        assert deleted_user.id == test_user.id
        
        # User should be deleted
        assert user_service.get(db_session, user_id=test_user.id) is None
        
        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "user_events"
        assert message["value"]["event_type"] == "deleted"
    
    def test_authenticate_user_success(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
    ):
        """Test authenticating a user with correct credentials."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        authenticated_user = user_service.authenticate(
            db_session, email=test_user.email, password="password123"
        )
        
        # Assert
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id
    
    def test_authenticate_user_wrong_password(
        self,
        db_session: Session,
        user_repository: UserRepository,
        test_user: User,
    ):
        """Test authenticating a user with wrong password."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        authenticated_user = user_service.authenticate(
            db_session, email=test_user.email, password="wrongpassword"
        )
        
        # Assert
        assert authenticated_user is None
    
    def test_authenticate_user_nonexistent(
        self,
        db_session: Session,
        user_repository: UserRepository,
    ):
        """Test authenticating a nonexistent user."""
        # Arrange
        user_service = UserService(repository=user_repository)
        
        # Act
        authenticated_user = user_service.authenticate(
            db_session, email="nonexistent@example.com", password="password123"
        )
        
        # Assert
        assert authenticated_user is None
