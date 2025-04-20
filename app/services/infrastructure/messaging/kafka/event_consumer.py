"""
Kafka event consumer for messaging.
"""
import logging
from typing import Any, Callable, Dict, List, Optional

from app.services.infrastructure.kafka.consumer import BaseKafkaConsumer

logger = logging.getLogger(__name__)


class EventConsumer(BaseKafkaConsumer):
    """
    Kafka consumer for receiving event messages.
    """
    
    def __init__(self, group_id: str = "event-consumer-group", **config_overrides):
        """
        Initialize event consumer.
        
        Args:
            group_id: Consumer group ID
            **config_overrides: Configuration overrides
        """
        super().__init__(group_id=group_id, **config_overrides)
        self._event_handlers = {}
    
    def register_event_handler(
        self,
        topic_key: str,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a handler for a specific event type on a topic.
        
        Args:
            topic_key: Topic key
            event_type: Type of event to handle
            handler: Function to handle events of this type
        """
        if topic_key not in self._event_handlers:
            self._event_handlers[topic_key] = {}
            
            # Register message handler for this topic
            self.register_handler(
                topic_key=topic_key,
                handler=lambda message: self._handle_event_message(topic_key, message)
            )
        
        self._event_handlers[topic_key][event_type] = handler
        logger.info(f"Registered handler for event type '{event_type}' on topic '{topic_key}'")
    
    def _handle_event_message(self, topic_key: str, message: Dict[str, Any]) -> None:
        """
        Handle an event message.
        
        Args:
            topic_key: Topic key
            message: Event message
        """
        try:
            event_type = message.get("event_type")
            if not event_type:
                logger.warning(f"Received message without event_type on topic '{topic_key}'")
                return
            
            # Find handler for this event type
            handlers = self._event_handlers.get(topic_key, {})
            handler = handlers.get(event_type)
            
            if handler:
                handler(message)
            else:
                logger.warning(f"No handler registered for event type '{event_type}' on topic '{topic_key}'")
        except Exception as e:
            logger.error(f"Error handling event message: {str(e)}")


# Global instance
event_consumer = EventConsumer()
