# Kiến trúc ứng dụng

Tài liệu này mô tả kiến trúc tổng thể của ứng dụng FastAPI E-commerce.

## Tổng quan kiến trúc

Ứng dụng được xây dựng theo kiến trúc sạch (Clean Architecture), tách biệt rõ ràng giữa các lớp nghiệp vụ và cơ sở hạ tầng. Kiến trúc này giúp ứng dụng dễ bảo trì, mở rộng và kiểm thử.

![Clean Architecture](https://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

## Các lớp kiến trúc

### 1. Lớp Domain (Models)

Lớp này chứa các entity và business rules cốt lõi của ứng dụng. Các entity được định nghĩa bằng SQLModel, kết hợp giữa SQLAlchemy và Pydantic.

**Vị trí**: `app/models/`

**Ví dụ**:
- `app/models/user.py`: Định nghĩa entity User
- `app/models/product.py`: Định nghĩa entity Product
- `app/models/order.py`: Định nghĩa entity Order

### 2. Lớp Application (Services)

Lớp này chứa business logic của ứng dụng, điều phối các entity để thực hiện các use case.

**Vị trí**: `app/services/business/`

**Ví dụ**:
- `app/services/business/user.py`: Xử lý logic liên quan đến người dùng
- `app/services/business/product.py`: Xử lý logic liên quan đến sản phẩm
- `app/services/business/order.py`: Xử lý logic liên quan đến đơn hàng

### 3. Lớp Infrastructure

Lớp này chứa các implementation cụ thể cho các interface được định nghĩa trong lớp Application, như database, messaging, caching, etc.

**Vị trí**: `app/services/infrastructure/`, `app/db/`

**Ví dụ**:
- `app/db/repositories/`: Data access layer
- `app/services/infrastructure/kafka/`: Kafka base module
- `app/services/infrastructure/messaging/`: Messaging services
- `app/services/infrastructure/async_tasks/`: Async task processing

### 4. Lớp Interface (API)

Lớp này chứa các API endpoints, xử lý request và response.

**Vị trí**: `app/api/`

**Ví dụ**:
- `app/api/routes/users.py`: API endpoints cho người dùng
- `app/api/routes/products.py`: API endpoints cho sản phẩm
- `app/api/routes/orders.py`: API endpoints cho đơn hàng

## Luồng dữ liệu

1. **Request** đi vào hệ thống thông qua API endpoints.
2. **API endpoints** chuyển request thành các tham số cho service.
3. **Service** thực hiện business logic, sử dụng repository để truy cập dữ liệu.
4. **Repository** tương tác với database để lấy hoặc lưu dữ liệu.
5. **Service** trả về kết quả cho API endpoint.
6. **API endpoint** chuyển kết quả thành response và trả về cho client.

## Xử lý bất đồng bộ

Ứng dụng sử dụng hai cơ chế xử lý bất đồng bộ:

### 1. Celery

Celery được sử dụng cho các tác vụ nền đơn giản, như import sản phẩm, gửi email, etc.

**Vị trí**: `app/services/infrastructure/async_tasks/celery/`

### 2. Kafka

Kafka được sử dụng cho các tác vụ phức tạp hơn, như xử lý sự kiện, streaming dữ liệu, etc.

**Vị trí**: 
- `app/services/infrastructure/kafka/`: Kafka base module
- `app/services/infrastructure/messaging/kafka/`: Kafka cho messaging
- `app/services/infrastructure/async_tasks/kafka/`: Kafka cho async tasks
- `app/services/infrastructure/streaming/kafka/`: Kafka cho streaming

## Messaging

Ứng dụng sử dụng Kafka để gửi và nhận các sự kiện trong hệ thống. Các sự kiện được phân loại thành các topic khác nhau:

- **Product Events**: Sự kiện liên quan đến sản phẩm (tạo, cập nhật, xóa)
- **Order Events**: Sự kiện liên quan đến đơn hàng (tạo, thanh toán, hủy)
- **User Events**: Sự kiện liên quan đến người dùng (đăng ký, cập nhật)

## Streaming

Ứng dụng sử dụng Kafka Streams để xử lý luồng dữ liệu thời gian thực, như phân tích hành vi người dùng, theo dõi tồn kho, etc.

## Bảo mật

Ứng dụng sử dụng JWT (JSON Web Token) để xác thực và phân quyền. Token được tạo khi người dùng đăng nhập và được sử dụng cho các request tiếp theo.

**Vị trí**: `app/core/security.py`

## Cấu hình

Cấu hình ứng dụng được quản lý thông qua các biến môi trường và file cấu hình.

**Vị trí**: `app/core/config.py`

## Kiểm thử

Ứng dụng có các test case cho các thành phần khác nhau:

- **Unit Tests**: Kiểm thử các thành phần riêng lẻ
- **Integration Tests**: Kiểm thử sự tương tác giữa các thành phần

**Vị trí**: `tests/`
