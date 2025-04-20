"""
Celery tasks for background processing.
"""
import json
import logging
from typing import Dict, List, Optional, Union

from celery import states
from celery.exceptions import Ignore

from app.services.infrastructure.tasks.celery_app import celery_app
from app.db.session import get_session
from app.core.deps import product_repository
from app.schemas.product import ProductCreate

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='import_products')
def import_products(
    self,
    products_data: List[Dict],
    user_id: int,
) -> Dict:
    """
    Import multiple products as a background task.

    Args:
        products_data: List of product data dictionaries
        user_id: ID of the user who initiated the import

    Returns:
        Dictionary with import results
    """
    total = len(products_data)
    processed = 0
    failed = 0
    failed_items = []

    # Update task state to STARTED
    self.update_state(
        state=states.STARTED,
        meta={
            "total": total,
            "processed": processed,
            "failed": failed,
        }
    )

    # Get database session
    session_generator = get_session()
    db = next(session_generator)

    try:
        for i, product_data in enumerate(products_data):
            try:
                # Create product schema
                product_in = ProductCreate(**product_data)

                # Create product in database
                product_repository.create(db, obj_in=product_in)

                processed += 1
            except Exception as e:
                logger.error(f"Error importing product: {str(e)}")
                failed += 1
                failed_items.append({
                    "data": product_data,
                    "error": str(e)
                })

            # Update progress every 10 items or on the last item
            if (i + 1) % 10 == 0 or i == total - 1:
                self.update_state(
                    state=states.STARTED,
                    meta={
                        "total": total,
                        "processed": processed,
                        "failed": failed,
                    }
                )

        # Return final result
        return {
            "status": "completed",
            "total": total,
            "processed": processed,
            "failed": failed,
            "failed_items": failed_items
        }
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        self.update_state(
            state=states.FAILURE,
            meta={
                "exc": str(e),
                "total": total,
                "processed": processed,
                "failed": failed,
            }
        )
        raise Ignore()
    finally:
        db.close()
