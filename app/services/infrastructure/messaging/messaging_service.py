"""
Service for handling messaging operations.
"""
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from app.core.config import settings
from app.services.infrastructure.messaging.kafka import kafka_client
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for messaging."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    PAYMENT_PROCESSED = "payment_processed"
    STOCK_UPDATED = "stock_updated"


class MessagingService:
    """Service for handling messaging operations."""
    
    def __init__(self):
        self.kafka_client = kafka_client
    
    def send_product_event(
        self, 
        product: Product, 
        event_type: EventType,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send product event to Kafka.
        
        Args:
            product: Product model
            event_type: Type of event
            additional_data: Additional data to include in the message
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Convert product to dict
            product_dict = product.model_dump()
            
            # Create message
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "product": product_dict,
            }
            
            # Add additional data if provided
            if additional_data:
                message.update(additional_data)
            
            # Send message
            return self.kafka_client.send_message(
                topic=settings.KAFKA_PRODUCT_TOPIC,
                value=message,
                key=f"product-{product.id}"
            )
        except Exception as e:
            logger.error(f"Failed to send product event: {str(e)}")
            return False
    
    def send_order_event(
        self, 
        order: Order, 
        event_type: EventType,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send order event to Kafka.
        
        Args:
            order: Order model
            event_type: Type of event
            additional_data: Additional data to include in the message
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Convert order to dict
            order_dict = order.model_dump()
            
            # Create message
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "order": order_dict,
            }
            
            # Add additional data if provided
            if additional_data:
                message.update(additional_data)
            
            # Send message
            return self.kafka_client.send_message(
                topic=settings.KAFKA_ORDER_TOPIC,
                value=message,
                key=f"order-{order.id}"
            )
        except Exception as e:
            logger.error(f"Failed to send order event: {str(e)}")
            return False
    
    def send_user_event(
        self, 
        user: User, 
        event_type: EventType,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send user event to Kafka.
        
        Args:
            user: User model
            event_type: Type of event
            additional_data: Additional data to include in the message
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Convert user to dict, excluding sensitive fields
            user_dict = user.model_dump(exclude={"hashed_password"})
            
            # Create message
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "user": user_dict,
            }
            
            # Add additional data if provided
            if additional_data:
                message.update(additional_data)
            
            # Send message
            return self.kafka_client.send_message(
                topic=settings.KAFKA_USER_TOPIC,
                value=message,
                key=f"user-{user.id}"
            )
        except Exception as e:
            logger.error(f"Failed to send user event: {str(e)}")
            return False
