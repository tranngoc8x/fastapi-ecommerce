from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.dependencies import get_current_active_user, get_current_admin_user, get_db, get_product_service
from app.models.user import User
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services.product import ProductService

router = APIRouter()


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    product_service: ProductService = Depends(get_product_service),
) -> Any:
    """
    Create new product (admin only).
    """
    return product_service.create(db, product_in=product_in)


@router.get("/", response_model=List[Product])
def read_products(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    product_service: ProductService = Depends(get_product_service),
) -> Any:
    """
    Retrieve products.
    """
    products = product_service.get_multi(
        db, skip=skip, limit=limit, active_only=active_only
    )
    return products


@router.get("/{product_id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> Any:
    """
    Get product by ID.
    """
    product = product_service.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is inactive",
        )

    return product


@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    product_service: ProductService = Depends(get_product_service),
) -> Any:
    """
    Update a product (admin only).
    """
    product = product_service.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_service.update(db, db_obj=product, obj_in=product_in)


@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    product_service: ProductService = Depends(get_product_service),
) -> Any:
    """
    Delete a product (admin only).
    """
    product = product_service.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_service.delete(db, product_id=product_id)
