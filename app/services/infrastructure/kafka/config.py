"""
Kafka configuration module.
"""
import logging
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaConfig:
    """
    Kafka configuration class.
    """
    # Default producer configuration
    DEFAULT_PRODUCER_CONFIG = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "acks": "all",
        "retries": 3,
        "max_in_flight_requests_per_connection": 1,
        "request_timeout_ms": 30000,
        "retry_backoff_ms": 500,
    }
    
    # Default consumer configuration
    DEFAULT_CONSUMER_CONFIG = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
        "auto_commit_interval_ms": 5000,
        "max_poll_records": 500,
        "max_poll_interval_ms": 300000,
        "session_timeout_ms": 30000,
        "heartbeat_interval_ms": 10000,
    }
    
    # Topic configuration
    TOPICS = {
        # Messaging topics
        "product_events": settings.KAFKA_PRODUCT_TOPIC,
        "order_events": settings.KAFKA_ORDER_TOPIC,
        "user_events": settings.KAFKA_USER_TOPIC,
        
        # Async tasks topics
        "async_tasks": settings.KAFKA_TASK_TOPIC,
        "task_results": settings.KAFKA_TASK_RESULT_TOPIC,
        
        # Streaming topics
        "stream_input": settings.KAFKA_STREAM_INPUT_TOPIC,
        "stream_output": settings.KAFKA_STREAM_OUTPUT_TOPIC,
    }
    
    @classmethod
    def get_producer_config(cls, **overrides) -> Dict[str, Any]:
        """
        Get producer configuration with optional overrides.
        
        Args:
            **overrides: Configuration overrides
            
        Returns:
            Producer configuration
        """
        config = cls.DEFAULT_PRODUCER_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_consumer_config(cls, group_id: str, **overrides) -> Dict[str, Any]:
        """
        Get consumer configuration with optional overrides.
        
        Args:
            group_id: Consumer group ID
            **overrides: Configuration overrides
            
        Returns:
            Consumer configuration
        """
        config = cls.DEFAULT_CONSUMER_CONFIG.copy()
        config["group_id"] = group_id
        config.update(overrides)
        return config
    
    @classmethod
    def get_topic(cls, topic_key: str) -> str:
        """
        Get topic name by key.
        
        Args:
            topic_key: Topic key
            
        Returns:
            Topic name
        """
        if topic_key not in cls.TOPICS:
            logger.warning(f"Unknown topic key: {topic_key}, using as-is")
            return topic_key
        
        return cls.TOPICS[topic_key]
