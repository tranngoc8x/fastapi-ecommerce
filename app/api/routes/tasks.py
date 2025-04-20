"""
API routes for background tasks.
"""
import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.database import get_db
from app.services.infrastructure.async_tasks.celery.app import celery_app
from app.models.user import User
from app.services.infrastructure.async_tasks.celery.tasks import import_products

router = APIRouter()


@router.post("/import-products")
async def create_import_products_task(
    *,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create a background task to import multiple products from a JSON file.

    This endpoint accepts a JSON file containing a list of products and
    starts a background task to import them. The task ID is returned for
    tracking progress.

    The JSON file should contain a list of product objects with the following fields:
    - name: Product name (required)
    - description: Product description (required)
    - price: Product price (required)
    - stock: Initial stock quantity (required)
    - is_active: Whether the product is active (optional, default: true)

    Example JSON:
    ```json
    [
        {
            "name": "Product 1",
            "description": "Description for product 1",
            "price": 19.99,
            "stock": 100,
            "is_active": true
        },
        {
            "name": "Product 2",
            "description": "Description for product 2",
            "price": 29.99,
            "stock": 50
        }
    ]
    ```

    Returns:
        JSON with task_id, status, and total_products
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON files are supported",
        )

    try:
        # Read and parse JSON file
        contents = await file.read()
        products_data = json.loads(contents)

        if not isinstance(products_data, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON file must contain a list of products",
            )

        # Start Celery task
        task = import_products.delay(products_data, current_user.id)

        return {
            "task_id": task.id,
            "status": "started",
            "total_products": len(products_data),
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON file",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get the status of a background task.

    This endpoint returns the current status of a background task,
    including progress information for tasks in progress.

    Args:
        task_id: The ID of the task to check

    Returns:
        JSON with task status information
    """
    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        response = {
            "task_id": task_id,
            "status": task.state,
            "info": "Task is pending",
        }
    elif task.state == "STARTED":
        response = {
            "task_id": task_id,
            "status": task.state,
            "info": task.info,
        }
    elif task.state == "SUCCESS":
        response = {
            "task_id": task_id,
            "status": task.state,
            "result": task.result,
        }
    elif task.state == "FAILURE":
        response = {
            "task_id": task_id,
            "status": task.state,
            "error": str(task.info),
        }
    else:
        response = {
            "task_id": task_id,
            "status": task.state,
        }

    return response
