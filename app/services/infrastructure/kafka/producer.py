"""
Kafka base producer module.
"""
import json
import logging
from typing import Any, Dict, Optional, Union, Callable

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.services.infrastructure.kafka.config import KafkaConfig

logger = logging.getLogger(__name__)


class BaseKafkaProducer:
    """
    Base Kafka producer class.
    """
    _instances = {}  # Class-level dictionary to store instances
    
    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern per class (not shared between subclasses).
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(BaseKafkaProducer, cls).__new__(cls)
            cls._instances[cls]._initialized = False
        return cls._instances[cls]
    
    def __init__(
        self,
        value_serializer: Optional[Callable] = None,
        key_serializer: Optional[Callable] = None,
        **config_overrides
    ):
        """
        Initialize Kafka producer.
        
        Args:
            value_serializer: Function to serialize message values
            key_serializer: Function to serialize message keys
            **config_overrides: Configuration overrides
        """
        # Only initialize once
        if self._initialized:
            return
            
        self._producer = None
        
        # Default serializers
        if value_serializer is None:
            value_serializer = lambda v: json.dumps(v).encode('utf-8')
        
        if key_serializer is None:
            key_serializer = lambda k: k.encode('utf-8') if k else None
        
        # Get configuration
        config = KafkaConfig.get_producer_config(**config_overrides)
        config["value_serializer"] = value_serializer
        config["key_serializer"] = key_serializer
        
        self._initialize_producer(config)
        self._initialized = True
    
    def _initialize_producer(self, config: Dict[str, Any]) -> None:
        """
        Initialize Kafka producer with configuration.
        
        Args:
            config: Producer configuration
        """
        try:
            self._producer = KafkaProducer(**config)
            logger.info(f"Kafka producer initialized with bootstrap servers: {config['bootstrap_servers']}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self._producer = None
    
    def send(
        self,
        topic_key: str,
        value: Any,
        key: Optional[str] = None,
        headers: Optional[list] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
    ) -> bool:
        """
        Send message to Kafka topic.
        
        Args:
            topic_key: Topic key (will be resolved to actual topic name)
            value: Message value
            key: Message key
            headers: Message headers
            partition: Specific partition
            timestamp_ms: Message timestamp
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self._producer:
            logger.error("Kafka producer not initialized")
            return False
        
        # Resolve topic name
        topic = KafkaConfig.get_topic(topic_key)
        
        try:
            future = self._producer.send(
                topic=topic,
                value=value,
                key=key,
                headers=headers,
                partition=partition,
                timestamp_ms=timestamp_ms
            )
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message sent to topic={record_metadata.topic} "
                f"partition={record_metadata.partition} "
                f"offset={record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending message to Kafka: {str(e)}")
            return False
    
    def flush(self, timeout: Optional[float] = None) -> None:
        """
        Flush all accumulated messages.
        
        Args:
            timeout: Maximum time to block in seconds
        """
        if self._producer:
            self._producer.flush(timeout=timeout)
    
    def close(self) -> None:
        """
        Close Kafka producer.
        """
        if self._producer:
            self._producer.close()
            logger.info("Kafka producer closed")
            self._producer = None
