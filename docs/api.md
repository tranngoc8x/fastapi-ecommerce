# API Documentation

Tài liệu này mô tả các API endpoints của ứng dụng FastAPI E-commerce.

## Base URL

```
http://localhost:8000
```

## Authentication

Hầu hết các endpoints yêu cầu xác thực bằng JWT token. Token được gửi trong header `Authorization` với prefix `Bearer`.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Lấy token

```
POST /api/auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Users API

### Đăng ký người dùng mới

```
POST /api/users
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Lấy thông tin người dùng hiện tại

```
GET /api/users/me
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Cập nhật thông tin người dùng

```
PUT /api/users/me
```

**Request Body**:
```json
{
  "full_name": "John Smith"
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Smith",
  "is_active": true,
  "is_admin": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

## Products API

### Tạo sản phẩm mới (Admin only)

```
POST /api/products
```

**Request Body**:
```json
{
  "name": "Product 1",
  "description": "This is a product",
  "price": 19.99,
  "stock": 100,
  "image_url": "https://example.com/image.jpg"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Product 1",
  "description": "This is a product",
  "price": 19.99,
  "stock": 100,
  "image_url": "https://example.com/image.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Lấy danh sách sản phẩm

```
GET /api/products
```

**Query Parameters**:
- `skip`: Số lượng sản phẩm bỏ qua (default: 0)
- `limit`: Số lượng sản phẩm tối đa trả về (default: 100)
- `active_only`: Chỉ lấy sản phẩm đang hoạt động (default: true)

**Response**:
```json
[
  {
    "id": 1,
    "name": "Product 1",
    "description": "This is a product",
    "price": 19.99,
    "stock": 100,
    "image_url": "https://example.com/image.jpg",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

### Lấy chi tiết sản phẩm

```
GET /api/products/{product_id}
```

**Response**:
```json
{
  "id": 1,
  "name": "Product 1",
  "description": "This is a product",
  "price": 19.99,
  "stock": 100,
  "image_url": "https://example.com/image.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Cập nhật sản phẩm (Admin only)

```
PUT /api/products/{product_id}
```

**Request Body**:
```json
{
  "price": 29.99,
  "stock": 50
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Product 1",
  "description": "This is a product",
  "price": 29.99,
  "stock": 50,
  "image_url": "https://example.com/image.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Xóa sản phẩm (Admin only)

```
DELETE /api/products/{product_id}
```

**Response**:
```json
{
  "id": 1,
  "name": "Product 1",
  "description": "This is a product",
  "price": 29.99,
  "stock": 50,
  "image_url": "https://example.com/image.jpg",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Import nhiều sản phẩm (Admin only)

```
POST /api/products/import
```

**Request Body**:
```json
{
  "products": [
    {
      "name": "Product 1",
      "description": "This is a product",
      "price": 19.99,
      "stock": 100,
      "image_url": "https://example.com/image.jpg"
    },
    {
      "name": "Product 2",
      "description": "This is another product",
      "price": 29.99,
      "stock": 50,
      "image_url": "https://example.com/image2.jpg"
    }
  ]
}
```

**Response**:
```json
{
  "task_id": "12345678-1234-5678-1234-567812345678",
  "status": "pending"
}
```

### Kiểm tra trạng thái import sản phẩm

```
GET /api/tasks/{task_id}
```

**Response**:
```json
{
  "task_id": "12345678-1234-5678-1234-567812345678",
  "status": "completed",
  "result": {
    "total": 2,
    "processed": 2,
    "failed": 0,
    "failed_items": []
  }
}
```

## Orders API

### Tạo đơn hàng mới

```
POST /api/orders
```

**Request Body**:
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 19.99
    }
  ]
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "total_amount": 39.98,
  "payment_id": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": 19.99
    }
  ]
}
```

### Lấy danh sách đơn hàng của người dùng

```
GET /api/orders
```

**Query Parameters**:
- `skip`: Số lượng đơn hàng bỏ qua (default: 0)
- `limit`: Số lượng đơn hàng tối đa trả về (default: 100)

**Response**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "pending",
    "total_amount": 39.98,
    "payment_id": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00",
    "items": [
      {
        "id": 1,
        "order_id": 1,
        "product_id": 1,
        "quantity": 2,
        "unit_price": 19.99
      }
    ]
  }
]
```

### Lấy chi tiết đơn hàng

```
GET /api/orders/{order_id}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "total_amount": 39.98,
  "payment_id": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": 19.99
    }
  ]
}
```

### Xử lý thanh toán đơn hàng

```
POST /api/orders/{order_id}/pay
```

**Request Body**:
```json
{
  "payment_id": "payment_12345"
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "paid",
  "total_amount": 39.98,
  "payment_id": "payment_12345",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": 19.99
    }
  ]
}
```

## Kafka Test API

### Gửi tin nhắn đến Kafka

```
POST /api/kafka/send
```

**Request Body**:
```json
{
  "topic": "test-topic",
  "key": "test-key",
  "value": {
    "message": "Hello, Kafka!"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Message sent to Kafka"
}
```

## Error Responses

Khi có lỗi xảy ra, API sẽ trả về response với status code tương ứng và body chứa thông tin lỗi.

**Example**:
```json
{
  "detail": "Not found"
}
```

**Common Status Codes**:
- `400 Bad Request`: Request không hợp lệ
- `401 Unauthorized`: Không có quyền truy cập
- `403 Forbidden`: Không có quyền thực hiện hành động
- `404 Not Found`: Không tìm thấy tài nguyên
- `422 Unprocessable Entity`: Dữ liệu không hợp lệ
- `500 Internal Server Error`: Lỗi server
