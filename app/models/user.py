from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.core.security import get_password_hash, verify_password


class User(SQLModel, table=True):
    """User database model."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    orders: List["Order"] = Relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return verify_password(password, self.hashed_password)

    @classmethod
    def create(cls, *, email: str, password: str, full_name: str) -> "User":
        """Create a new user with hashed password."""
        hashed_password = get_password_hash(password)
        return cls(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
