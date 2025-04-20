from typing import Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for user operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session
            email: Email of the user to get
            
        Returns:
            The user if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            obj_in: Schema with user data
            
        Returns:
            Created user
        """
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """
        Update a user, handling password hashing if needed.
        
        Args:
            db: Database session
            db_obj: User to update
            obj_in: Schema with update data
            
        Returns:
            Updated user
        """
        update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            Authenticated user if credentials are valid, None otherwise
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        
        if not user.verify_password(password):
            return None
        
        return user
