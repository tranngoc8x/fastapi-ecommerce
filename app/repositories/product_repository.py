from typing import List

from sqlmodel import Session, select

from app.models.product import Product
from app.repositories.base_repository import BaseRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    """Repository for product operations."""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Product]:
        """
        Get multiple products with optional filtering for active only.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: If True, only return active products
            
        Returns:
            List of products
        """
        statement = select(Product)
        
        if active_only:
            statement = statement.where(Product.is_active == True)
            
        statement = statement.offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def update_stock(self, db: Session, *, product_id: int, quantity: int) -> Product:
        """
        Update product stock.
        
        Args:
            db: Database session
            product_id: ID of the product to update
            quantity: Quantity to add (positive) or remove (negative) from stock
            
        Returns:
            Updated product
        """
        product = self.get(db, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.stock += quantity
        
        if product.stock < 0:
            raise ValueError(f"Insufficient stock for product {product_id}")
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
