from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.dependencies import get_current_active_user, get_current_admin_user, get_db, get_order_service
from app.models.user import User
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderWithUser
from app.services.order import OrderService

router = APIRouter()


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Create new order.
    """
    # Ensure user can only create orders for themselves
    if order_in.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create order for another user",
        )

    try:
        return order_service.create(db, order_in=order_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[Order])
def read_orders(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Retrieve orders.
    """
    # Regular users can only see their own orders
    if current_user.is_admin:
        return order_service.get_multi(db, skip=skip, limit=limit)
    else:
        return order_service.get_multi(
            db, user_id=current_user.id, skip=skip, limit=limit
        )


@router.get("/admin", response_model=List[OrderWithUser])
def read_all_orders(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Retrieve all orders with user information (admin only).
    """
    return order_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Get order by ID.
    """
    order = order_service.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Regular users can only see their own orders
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this order",
        )

    return order


@router.put("/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Update an order (admin only).
    """
    order = order_service.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_service.update(db, db_obj=order, obj_in=order_in)


@router.post("/{order_id}/pay", response_model=Order)
def process_payment(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    payment_id: str,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Process payment for an order.
    """
    order = order_service.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Regular users can only pay for their own orders
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to pay for this order",
        )

    try:
        return order_service.process_payment(db, order_id=order_id, payment_id=payment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{order_id}", response_model=Order)
def delete_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
) -> Any:
    """
    Delete an order (admin only).
    """
    order = order_service.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_service.delete(db, order_id=order_id)
