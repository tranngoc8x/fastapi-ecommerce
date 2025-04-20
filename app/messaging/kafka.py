"""
Kafka producer module.
"""
import json
import logging
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaClient:
    """
    Kafka client for producing messages.
    """
    _instance = None
    _producer = None

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of KafkaClient is created.
        """
        if cls._instance is None:
            cls._instance = super(KafkaClient, cls).__new__(cls)
            cls._instance._initialize_producer()
        return cls._instance

    def _initialize_producer(self) -> None:
        """
        Initialize Kafka producer.
        """
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1,
            )
            logger.info(f"Kafka producer initialized with bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self._producer = None

    def send_message(
        self, 
        topic: str, 
        value: Dict[str, Any], 
        key: Optional[str] = None,
        headers: Optional[list] = None
    ) -> bool:
        """
        Send message to Kafka topic.
        
        Args:
            topic: Kafka topic
            value: Message value (will be serialized to JSON)
            key: Message key (optional)
            headers: Message headers (optional)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self._producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            future = self._producer.send(
                topic=topic,
                value=value,
                key=key,
                headers=headers
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

    def close(self) -> None:
        """
        Close Kafka producer.
        """
        if self._producer:
            self._producer.close()
            logger.info("Kafka producer closed")


# Global instance
kafka_client = KafkaClient()
