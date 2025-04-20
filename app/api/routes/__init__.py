from fastapi import APIRouter

from app.api.routes import auth, users, products, orders, tasks, kafka_test

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(kafka_test.router, prefix="/kafka", tags=["kafka"])