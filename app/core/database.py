import time
from typing import Generator

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(str(settings.DATABASE_URL), echo=settings.DEBUG)


def create_db_and_tables() -> None:
    """Create database tables from SQLModel metadata."""
    # Add retry logic for database connection
    max_retries = 5
    retry_count = 0
    retry_delay = 2  # seconds

    while retry_count < max_retries:
        try:
            SQLModel.metadata.create_all(engine)
            print("Successfully connected to the database and created tables.")
            return
        except OperationalError as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"Database connection failed. Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff
            else:
                print(f"Failed to connect to the database after {max_retries} attempts.")
                # In development, we might want to continue even if DB is not available initially
                if settings.ENVIRONMENT == "development":
                    print("Running in development mode. Continuing without database.")
                    return
                raise


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    with Session(engine) as session:
        yield session
