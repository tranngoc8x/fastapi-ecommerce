"""
Kafka event producer for messaging.
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.infrastructure.kafka.producer import BaseKafkaProducer

logger = logging.getLogger(__name__)


class EventProducer(BaseKafkaProducer):
    """
    Kafka producer for sending event messages.
    """
    
    def send_event(
        self,
        topic_key: str,
        event_type: str,
        data: Dict[str, Any],
        entity_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an event message to Kafka.
        
        Args:
            topic_key: Topic key
            event_type: Type of event
            data: Event data
            entity_id: ID of the entity (for message key)
            additional_data: Additional data to include in the message
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Create message
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            }
            
            # Add additional data if provided
            if additional_data:
                message.update(additional_data)
            
            # Generate key if entity_id provided
            key = f"{topic_key}-{entity_id}" if entity_id else None
            
            # Send message
            return self.send(
                topic_key=topic_key,
                value=message,
                key=key
            )
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            return False


# Global instance
event_producer = EventProducer()
