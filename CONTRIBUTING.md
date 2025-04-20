# Hướng dẫn đóng góp

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án FastAPI E-commerce! Dưới đây là hướng dẫn để giúp bạn đóng góp hiệu quả.

## Quy trình đóng góp

1. Fork repository
2. Clone repository đã fork về máy local
3. Tạo branch mới cho tính năng hoặc fix của bạn
4. Viết code và tests
5. Commit và push code lên repository của bạn
6. Tạo Pull Request

## Chuẩn bị môi trường phát triển

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-ecommerce.git
   cd fastapi-ecommerce
   ```

2. Khởi động các dịch vụ với Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Chạy migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. Tạo user admin đầu tiên:
   ```bash
   docker-compose exec api python -m app.initial_data
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

## Viết tests

Mỗi tính năng mới hoặc fix phải có tests đi kèm. Chúng tôi sử dụng pytest cho việc testing.

### Unit tests

Unit tests nên được đặt trong thư mục `tests/unit/` và tên file nên bắt đầu bằng `test_`.

```python
# tests/unit/services/business/test_user_service.py
def test_create_user(db_session, user_repository):
    """Test creating a user."""
    # Arrange
    user_service = UserService(repository=user_repository)
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
    }
    user_in = UserCreate(**user_data)
    
    # Act
    user = user_service.create(db_session, user_in=user_in)
    
    # Assert
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]
```

### Integration tests

Integration tests nên được đặt trong thư mục `tests/integration/` và tên file nên bắt đầu bằng `test_`.

```python
# tests/integration/services/test_kafka_integration.py
@pytest.mark.integration
def test_kafka_integration(mock_kafka_producer_class):
    """Test integration between producer and consumer."""
    # Arrange
    # ...
    
    # Act
    # ...
    
    # Assert
    # ...
```

### Chạy tests

```bash
# Chạy tất cả tests
docker-compose exec api pytest

# Chạy unit tests
docker-compose exec api pytest tests/unit/

# Chạy integration tests
docker-compose exec api pytest tests/integration/

# Chạy một file test cụ thể
docker-compose exec api pytest tests/unit/services/business/test_user_service.py

# Chạy một test cụ thể
docker-compose exec api pytest tests/unit/services/business/test_user_service.py::test_create_user
```

## Commit Messages

Commit messages nên tuân theo format sau:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Trong đó:
- `<type>`: feat, fix, docs, style, refactor, test, chore
- `<scope>`: api, models, services, etc.
- `<subject>`: Mô tả ngắn gọn về commit
- `<body>`: Mô tả chi tiết về commit (optional)
- `<footer>`: Thông tin về breaking changes hoặc issues đã fix (optional)

Ví dụ:
```
feat(user): add user registration endpoint

Add endpoint for user registration with email verification.

Closes #123
```

## Pull Requests

- Mỗi Pull Request nên tập trung vào một tính năng hoặc fix cụ thể
- Mô tả chi tiết về tính năng hoặc fix trong Pull Request
- Đảm bảo tất cả tests đều pass
- Đảm bảo code đã được format theo coding standards
- Đảm bảo không có lỗi type checking
- Đảm bảo không có lỗi linting

## Báo cáo lỗi

Nếu bạn tìm thấy lỗi, vui lòng báo cáo bằng cách tạo issue mới với các thông tin sau:

- Mô tả ngắn gọn về lỗi
- Các bước để tái hiện lỗi
- Kết quả mong đợi
- Kết quả thực tế
- Môi trường (hệ điều hành, phiên bản Docker, etc.)
- Screenshots (nếu có)

## Đề xuất tính năng mới

Nếu bạn muốn đề xuất tính năng mới, vui lòng tạo issue mới với các thông tin sau:

- Mô tả ngắn gọn về tính năng
- Lý do tại sao tính năng này hữu ích
- Cách tính năng này sẽ hoạt động
- Các tính năng tương tự ở các dự án khác (nếu có)

## Liên hệ

Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ với chúng tôi qua email hoặc tạo issue mới.

Cảm ơn bạn đã đóng góp cho dự án FastAPI E-commerce!
