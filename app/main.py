from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.db.session import create_db_and_tables

# Tạo ứng dụng FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="E-commerce API with FastAPI and SQLModel",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cấu hình CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Khởi tạo cơ sở dữ liệu khi ứng dụng khởi động
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce API"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include API router
app.include_router(api_router, prefix="/api")
