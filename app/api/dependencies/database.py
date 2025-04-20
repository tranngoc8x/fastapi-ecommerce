from typing import Generator

from sqlmodel import Session

from app.db.session import get_session


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()
