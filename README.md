# E-commerce API with FastAPI

API quản lý sản phẩm, đơn hàng và xử lý thanh toán sử dụng FastAPI, SQLModel, Kafka và Celery.

## Tổng quan

FastAPI E-commerce là một ứng dụng backend RESTful API cho nền tảng thương mại điện tử, cung cấp các chức năng quản lý người dùng, sản phẩm và đơn hàng. Ứng dụng được thiết kế với kiến trúc sạch (Clean Architecture), tách biệt rõ ràng giữa các lớp nghiệp vụ và cơ sở hạ tầng.

## Tính năng

- **Quản lý người dùng**: Đăng ký, đăng nhập, quản lý thông tin người dùng
- **Quản lý sản phẩm**: CRUD sản phẩm, quản lý kho
- **Quản lý đơn hàng**: Tạo đơn hàng, xử lý thanh toán
- **Xử lý bất đồng bộ**: Sử dụng Celery và Kafka cho các tác vụ nền
- **Messaging**: Gửi thông báo và sự kiện qua Kafka
- **Streaming**: Xử lý luồng dữ liệu thời gian thực

## Công nghệ

- **FastAPI**: Framework API hiệu suất cao
- **SQLModel**: ORM kết hợp SQLAlchemy và Pydantic
- **PostgreSQL**: Cơ sở dữ liệu quan hệ
- **Kafka**: Nền tảng xử lý luồng dữ liệu phân tán
- **Celery**: Hệ thống xử lý tác vụ bất đồng bộ
- **Redis**: Cache và message broker
- **Docker**: Container hóa ứng dụng
- **JWT**: Xác thực và phân quyền

## Cấu trúc dự án

```
fast-api/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Cấu hình ứng dụng
│   ├── models/         # Mô hình dữ liệu
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── utils/          # Tiện ích
├── tests/              # Unit tests
├── .env                # Biến môi trường
├── docker-compose.yml  # Cấu hình Docker Compose
├── Dockerfile          # Cấu hình Docker
└── pyproject.toml      # Cấu hình dự án
```

## Tài liệu

Tài liệu chi tiết có thể được tìm thấy trong thư mục `docs/`:

- [Kiến trúc](docs/architecture.md): Mô tả kiến trúc tổng thể của ứng dụng
- [API](docs/api.md): Tài liệu API
- [Phát triển](docs/development.md): Hướng dẫn phát triển
- [Triển khai](docs/deployment.md): Hướng dẫn triển khai

## Yêu cầu

- Docker
- Docker Compose

## Cài đặt và chạy

1. Clone repository:

```bash
git clone <repository-url>
cd fast-api
```

2. Khởi động ứng dụng với Docker Compose:

```bash
docker-compose up -d
```

3. Truy cập API:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - PgAdmin: http://localhost:5050 (Email: admin@admin.com, Password: admin)

## Phát triển

### Tạo migration

```bash
docker-compose exec api alembic revision --autogenerate -m "message"
```

### Chạy migration

```bash
docker-compose exec api alembic upgrade head
```

### Chạy tests

```bash
docker-compose exec api pytest
```

## API Endpoints

### Users
- `POST /api/users`: Đăng ký người dùng mới
- `GET /api/users/me`: Lấy thông tin người dùng hiện tại
- `PUT /api/users/me`: Cập nhật thông tin người dùng
- `POST /api/auth/login`: Đăng nhập và lấy token
- `POST /api/auth/refresh`: Làm mới token

### Products
- `POST /api/products`: Tạo sản phẩm mới (admin)
- `GET /api/products`: Lấy danh sách sản phẩm
- `GET /api/products/{product_id}`: Lấy chi tiết sản phẩm
- `PUT /api/products/{product_id}`: Cập nhật sản phẩm (admin)
- `DELETE /api/products/{product_id}`: Xóa sản phẩm (admin)

### Orders
- `POST /api/orders`: Tạo đơn hàng mới
- `GET /api/orders`: Lấy danh sách đơn hàng của người dùng
- `GET /api/orders/{order_id}`: Lấy chi tiết đơn hàng
- `PUT /api/orders/{order_id}`: Cập nhật trạng thái đơn hàng (admin)
- `POST /api/orders/{order_id}/pay`: Xử lý thanh toán đơn hàng
