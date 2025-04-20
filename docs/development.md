# Hướng dẫn phát triển

Tài liệu này cung cấp hướng dẫn chi tiết để phát triển ứng dụng FastAPI E-commerce.

## Cài đặt môi trường phát triển

### Yêu cầu

- Docker và Docker Compose
- Python 3.9+
- Git

### Cài đặt

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-ecommerce.git
   cd fastapi-ecommerce
   ```

2. Khởi động các dịch vụ với Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. API sẽ có sẵn tại: http://localhost:8000

4. Tài liệu API (Swagger UI): http://localhost:8000/docs

## Cấu trúc dự án

```
app/
├── api/                    # API endpoints
│   ├── deps.py             # API dependencies
│   ├── routes/             # API routes
├── core/                   # Core modules
│   ├── config.py           # Application configuration
│   ├── security.py         # Security utilities
├── db/                     # Database
│   ├── repositories/       # Data access layer
│   ├── session.py          # Database session
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Service layer
│   ├── business/           # Business services
│   └── infrastructure/     # Infrastructure services
│       ├── async_tasks/    # Async task processing
│       │   ├── celery/     # Celery implementation
│       │   └── kafka/      # Kafka implementation
│       ├── kafka/          # Kafka base module
│       ├── messaging/      # Messaging services
│       └── streaming/      # Streaming services
└── main.py                 # Application entry point
```

## Quy trình phát triển

### 1. Tạo branch mới

```bash
git checkout -b feature/your-feature-name
```

### 2. Viết code

Tuân thủ các quy tắc và cấu trúc đã được thiết lập trong dự án.

### 3. Chạy tests

```bash
docker-compose exec api pytest
```

### 4. Commit và push

```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

### 5. Tạo Pull Request

Tạo Pull Request trên GitHub và chờ review.

## Database Migrations

### Tạo migration

```bash
docker-compose exec api alembic revision --autogenerate -m "message"
```

### Chạy migration

```bash
docker-compose exec api alembic upgrade head
```

## Thêm model mới

### 1. Tạo database model

Tạo file mới trong thư mục `app/models/`:

```python
# app/models/new_model.py
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NewModel(SQLModel, table=True):
    """New model."""
    
    __tablename__ = "new_models"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Tạo Pydantic schema

Tạo file mới trong thư mục `app/schemas/`:

```python
# app/schemas/new_model.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewModelBase(BaseModel):
    """Base new model schema."""
    name: str
    description: str


class NewModelCreate(NewModelBase):
    """New model creation schema."""
    pass


class NewModelUpdate(BaseModel):
    """New model update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class NewModelInDBBase(NewModelBase):
    """New model in DB base schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewModel(NewModelInDBBase):
    """New model schema for API responses."""
    pass
```

### 3. Tạo repository

Tạo file mới trong thư mục `app/db/repositories/`:

```python
# app/db/repositories/new_model_repository.py
from app.db.repositories.base_repository import BaseRepository
from app.models.new_model import NewModel
from app.schemas.new_model import NewModelCreate, NewModelUpdate


class NewModelRepository(BaseRepository[NewModel, NewModelCreate, NewModelUpdate]):
    """Repository for new model operations."""
    
    def __init__(self):
        super().__init__(NewModel)
```

### 4. Tạo service

Tạo file mới trong thư mục `app/services/business/`:

```python
# app/services/business/new_model.py
from typing import List, Optional

from sqlmodel import Session

from app.db.repositories.new_model_repository import NewModelRepository
from app.models.new_model import NewModel
from app.schemas.new_model import NewModelCreate, NewModelUpdate
from app.services.infrastructure.messaging.service import EventType, MessagingService


class NewModelService:
    """Service for new model operations."""
    
    def __init__(
        self,
        repository: NewModelRepository = NewModelRepository(),
        messaging_service: MessagingService = MessagingService(),
    ):
        self.repository = repository
        self.messaging_service = messaging_service
    
    def create(self, db: Session, *, new_model_in: NewModelCreate) -> NewModel:
        """
        Create a new model.
        
        Args:
            db: Database session
            new_model_in: New model data
            
        Returns:
            Created new model
        """
        new_model = self.repository.create(db, obj_in=new_model_in)
        
        # Send event to Kafka
        self.messaging_service.send_event(
            topic_key="new_model_events",
            event_type=EventType.CREATED,
            data=new_model.model_dump(),
            entity_id=str(new_model.id),
        )
        
        return new_model
    
    def get(self, db: Session, *, new_model_id: int) -> Optional[NewModel]:
        """
        Get a new model by ID.
        
        Args:
            db: Database session
            new_model_id: New model ID
            
        Returns:
            New model if found, None otherwise
        """
        return self.repository.get(db, id=new_model_id)
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[NewModel]:
        """
        Get multiple new models.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only return active new models
            
        Returns:
            List of new models
        """
        if active_only:
            return self.repository.get_multi_by_filter(
                db, skip=skip, limit=limit, filter_dict={"is_active": True}
            )
        return self.repository.get_multi(db, skip=skip, limit=limit)
    
    def update(
        self, db: Session, *, db_obj: NewModel, obj_in: NewModelUpdate
    ) -> NewModel:
        """
        Update a new model.
        
        Args:
            db: Database session
            db_obj: New model to update
            obj_in: New model update data
            
        Returns:
            Updated new model
        """
        updated_new_model = self.repository.update(db, db_obj=db_obj, obj_in=obj_in)
        
        # Send event to Kafka
        self.messaging_service.send_event(
            topic_key="new_model_events",
            event_type=EventType.UPDATED,
            data=updated_new_model.model_dump(),
            entity_id=str(updated_new_model.id),
        )
        
        return updated_new_model
    
    def delete(self, db: Session, *, new_model_id: int) -> Optional[NewModel]:
        """
        Delete a new model.
        
        Args:
            db: Database session
            new_model_id: New model ID
            
        Returns:
            Deleted new model if found, None otherwise
        """
        new_model = self.repository.get(db, id=new_model_id)
        if not new_model:
            return None
        
        deleted_new_model = self.repository.remove(db, id=new_model_id)
        
        # Send event to Kafka
        self.messaging_service.send_event(
            topic_key="new_model_events",
            event_type=EventType.DELETED,
            data=deleted_new_model.model_dump(),
            entity_id=str(deleted_new_model.id),
        )
        
        return deleted_new_model
```

### 5. Tạo API endpoints

Tạo file mới trong thư mục `app/api/routes/`:

```python
# app/api/routes/new_models.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_active_user, get_current_admin_user, get_db
from app.models.new_model import NewModel
from app.models.user import User
from app.schemas.new_model import NewModelCreate, NewModelUpdate
from app.services.business.new_model import NewModelService

router = APIRouter()
new_model_service = NewModelService()


@router.post("/", response_model=NewModel, status_code=status.HTTP_201_CREATED)
def create_new_model(
    *,
    db: Session = Depends(get_db),
    new_model_in: NewModelCreate,
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new model.
    """
    new_model = new_model_service.create(db, new_model_in=new_model_in)
    return new_model


@router.get("/", response_model=List[NewModel])
def read_new_models(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get multiple new models.
    """
    new_models = new_model_service.get_multi(
        db, skip=skip, limit=limit, active_only=active_only
    )
    return new_models


@router.get("/{new_model_id}", response_model=NewModel)
def read_new_model(
    *,
    db: Session = Depends(get_db),
    new_model_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a new model by ID.
    """
    new_model = new_model_service.get(db, new_model_id=new_model_id)
    if not new_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New model not found",
        )
    return new_model


@router.put("/{new_model_id}", response_model=NewModel)
def update_new_model(
    *,
    db: Session = Depends(get_db),
    new_model_id: int,
    new_model_in: NewModelUpdate,
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a new model.
    """
    new_model = new_model_service.get(db, new_model_id=new_model_id)
    if not new_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New model not found",
        )
    new_model = new_model_service.update(db, db_obj=new_model, obj_in=new_model_in)
    return new_model


@router.delete("/{new_model_id}", response_model=NewModel)
def delete_new_model(
    *,
    db: Session = Depends(get_db),
    new_model_id: int,
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a new model.
    """
    new_model = new_model_service.delete(db, new_model_id=new_model_id)
    if not new_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New model not found",
        )
    return new_model
```

### 6. Đăng ký router

Thêm router vào file `app/api/api.py`:

```python
from app.api.routes import new_models

api_router.include_router(new_models.router, prefix="/new-models", tags=["new-models"])
```

### 7. Tạo migration

```bash
docker-compose exec api alembic revision --autogenerate -m "Add new model"
docker-compose exec api alembic upgrade head
```

## Thêm Kafka topic mới

### 1. Cập nhật cấu hình

Thêm topic mới vào file `app/core/config.py`:

```python
# Kafka topics
KAFKA_NEW_MODEL_TOPIC: str = os.getenv("KAFKA_NEW_MODEL_TOPIC", "new-model-events")
```

### 2. Cập nhật KafkaConfig

Thêm topic mới vào `app/services/infrastructure/kafka/config.py`:

```python
# Topic configuration
TOPICS = {
    # Existing topics...
    
    # New topic
    "new_model_events": settings.KAFKA_NEW_MODEL_TOPIC,
}
```

### 3. Tạo consumer cho topic mới

```python
# app/services/infrastructure/messaging/kafka/new_model_consumer.py
import logging
from typing import Dict, Any, Callable

from app.services.infrastructure.kafka.consumer import BaseKafkaConsumer

logger = logging.getLogger(__name__)


class NewModelConsumer(BaseKafkaConsumer):
    """
    Kafka consumer for new model events.
    """
    
    def __init__(self, group_id: str = "new-model-consumer-group", **config_overrides):
        """
        Initialize new model consumer.
        
        Args:
            group_id: Consumer group ID
            **config_overrides: Configuration overrides
        """
        super().__init__(group_id=group_id, **config_overrides)
        self._event_handlers = {}
    
    def register_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to handle events of this type
        """
        self._event_handlers[event_type] = handler
        logger.info(f"Registered handler for event type '{event_type}'")
        
        # Register message handler for the topic
        if not self._handlers:
            self.register_handler(
                topic_key="new_model_events",
                handler=self._handle_event_message
            )
    
    def _handle_event_message(self, message: Dict[str, Any]) -> None:
        """
        Handle an event message.
        
        Args:
            message: Event message
        """
        try:
            event_type = message.get("event_type")
            if not event_type:
                logger.warning("Received message without event_type")
                return
            
            # Find handler for this event type
            handler = self._event_handlers.get(event_type)
            
            if handler:
                handler(message)
            else:
                logger.warning(f"No handler registered for event type '{event_type}'")
        except Exception as e:
            logger.error(f"Error handling event message: {str(e)}")


# Global instance
new_model_consumer = NewModelConsumer()
```

### 4. Sử dụng consumer

```python
# Example usage
from app.services.infrastructure.messaging.kafka.new_model_consumer import new_model_consumer

def handle_new_model_created(message):
    print(f"New model created: {message}")

new_model_consumer.register_event_handler("created", handle_new_model_created)
new_model_consumer.start()
```

## Thêm Celery task mới

### 1. Tạo task mới

Thêm task mới vào file `app/services/infrastructure/async_tasks/celery/tasks.py`:

```python
@celery_app.task(bind=True, name='process_new_model')
def process_new_model(self, new_model_id: int) -> Dict:
    """
    Process a new model as a background task.

    Args:
        new_model_id: ID of the new model to process

    Returns:
        Dictionary with processing results
    """
    # Update task state to STARTED
    self.update_state(
        state=states.STARTED,
        meta={
            "new_model_id": new_model_id,
            "status": "processing",
        }
    )

    # Get database session
    session_generator = get_session()
    db = next(session_generator)

    try:
        # Get the new model
        new_model = db.query(NewModel).filter(NewModel.id == new_model_id).first()
        if not new_model:
            raise ValueError(f"New model with ID {new_model_id} not found")

        # Process the new model
        # ...

        # Return result
        return {
            "status": "completed",
            "new_model_id": new_model_id,
            "result": "Processing completed successfully"
        }
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        self.update_state(
            state=states.FAILURE,
            meta={
                "exc": str(e),
                "new_model_id": new_model_id,
                "status": "failed",
            }
        )
        raise Ignore()
    finally:
        db.close()
```

### 2. Sử dụng task

```python
# Example usage
from app.services.infrastructure.async_tasks.celery.tasks import process_new_model

# Call the task
task = process_new_model.delay(new_model_id=1)
task_id = task.id
```

## Viết tests

### 1. Unit tests

Tạo file test mới trong thư mục `tests/unit/services/business/`:

```python
# tests/unit/services/business/test_new_model_service.py
import pytest
from sqlmodel import Session

from app.models.new_model import NewModel
from app.schemas.new_model import NewModelCreate, NewModelUpdate
from app.services.business.new_model import NewModelService
from app.db.repositories.new_model_repository import NewModelRepository


class TestNewModelService:
    """Test cases for NewModelService."""
    
    def test_create_new_model(
        self,
        db_session: Session,
        new_model_repository: NewModelRepository,
        mock_kafka_producer,
    ):
        """Test creating a new model."""
        # Arrange
        new_model_service = NewModelService(
            repository=new_model_repository,
        )
        new_model_data = {
            "name": "Test New Model",
            "description": "This is a test new model",
        }
        new_model_in = NewModelCreate(**new_model_data)
        
        # Act
        new_model = new_model_service.create(db_session, new_model_in=new_model_in)
        
        # Assert
        assert new_model.name == new_model_data["name"]
        assert new_model.description == new_model_data["description"]
        assert new_model.is_active
        
        # Check that a message was sent to Kafka
        assert len(mock_kafka_producer.messages) == 1
        message = mock_kafka_producer.messages[0]
        assert message["topic"] == "new_model_events"
        assert message["value"]["event_type"] == "created"
        assert message["value"]["data"]["name"] == new_model_data["name"]
```

### 2. Integration tests

Tạo file test mới trong thư mục `tests/integration/services/`:

```python
# tests/integration/services/test_new_model_integration.py
import pytest
from unittest.mock import patch

from app.services.infrastructure.kafka.producer import BaseKafkaProducer
from app.services.infrastructure.messaging.kafka.event_producer import EventProducer
from app.services.business.new_model import NewModelService
from app.schemas.new_model import NewModelCreate


@pytest.mark.integration
class TestNewModelIntegration:
    """Integration tests for NewModelService."""
    
    @patch("app.services.infrastructure.kafka.producer.KafkaProducer")
    def test_new_model_kafka_integration(
        self,
        mock_kafka_producer_class,
        db_session,
        new_model_repository,
    ):
        """Test integration between NewModelService and Kafka."""
        # Arrange
        # Mock the KafkaProducer to avoid actual Kafka connection
        mock_producer = mock_kafka_producer_class.return_value
        
        # Create a new model service
        new_model_service = NewModelService(
            repository=new_model_repository,
        )
        
        # Create a new model
        new_model_data = {
            "name": "Test New Model",
            "description": "This is a test new model",
        }
        new_model_in = NewModelCreate(**new_model_data)
        
        # Act
        new_model = new_model_service.create(db_session, new_model_in=new_model_in)
        
        # Assert
        assert new_model.name == new_model_data["name"]
        assert new_model.description == new_model_data["description"]
        
        # Check that the producer was called
        assert mock_producer.send.called
```

## Coding Standards

### Python Style Guide

- Tuân thủ [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Sử dụng [Black](https://github.com/psf/black) để format code
- Sử dụng [isort](https://github.com/PyCQA/isort) để sắp xếp imports
- Sử dụng [mypy](https://github.com/python/mypy) để kiểm tra type hints

### Docstrings

Sử dụng Google style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Function description.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this error is raised
    """
    pass
```

### Imports

Sắp xếp imports theo thứ tự:

1. Standard library imports
2. Related third party imports
3. Local application/library specific imports

```python
# Standard library imports
import json
from datetime import datetime
from typing import List, Optional

# Third party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

# Local imports
from app.api.deps import get_current_active_user
from app.models.user import User
```

### Error Handling

Sử dụng exceptions để xử lý lỗi:

```python
def get_user(db: Session, user_id: int) -> User:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
```

## Debugging

### Logging

Sử dụng logging để debug:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### FastAPI Debug Mode

Chạy FastAPI trong debug mode:

```bash
docker-compose exec api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Debugging với VSCode

1. Tạo file `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "jinja": true
        }
    ]
}
```

2. Đặt breakpoints trong code
3. Chạy debug session từ VSCode
