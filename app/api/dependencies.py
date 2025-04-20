from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import ALGORITHM
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.user import UserService
from app.services.product import ProductService
from app.services.order import OrderService
from app.core.deps import user_service, product_service, order_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()


def get_user_service() -> UserService:
    """Dependency for getting the user service."""
    return user_service


def get_product_service() -> ProductService:
    """Dependency for getting the product service."""
    return product_service


def get_order_service() -> OrderService:
    """Dependency for getting the order service."""
    return order_service


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Get the current user from the token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = user_service.get(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
