"""
Kafka consumer for async tasks.
"""
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaTaskConsumer:
    """
    Kafka consumer for processing async tasks.
    """
    _instance = None
    _consumer = None
    _running = False
    _thread = None
    _handlers = {}

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of KafkaTaskConsumer is created.
        """
        if cls._instance is None:
            cls._instance = super(KafkaTaskConsumer, cls).__new__(cls)
            cls._instance._initialize_consumer()
        return cls._instance

    def _initialize_consumer(self) -> None:
        """
        Initialize Kafka consumer.
        """
        try:
            self._consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='async-tasks-group',
            )
            logger.info(f"Kafka consumer initialized with bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            self._consumer = None

    def register_handler(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a handler for a specific topic.
        
        Args:
            topic: Kafka topic
            handler: Function to handle messages from this topic
        """
        self._handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")

    def start(self, topics: Optional[List[str]] = None) -> None:
        """
        Start consuming messages from Kafka.
        
        Args:
            topics: List of topics to subscribe to. If None, subscribes to all registered handlers.
        """
        if not self._consumer:
            logger.error("Kafka consumer not initialized")
            return

        if self._running:
            logger.warning("Kafka consumer already running")
            return

        # If no topics provided, use all registered handlers
        if topics is None:
            topics = list(self._handlers.keys())

        if not topics:
            logger.warning("No topics to subscribe to")
            return

        # Subscribe to topics
        self._consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")

        # Start consumer thread
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop)
        self._thread.daemon = True
        self._thread.start()
        logger.info("Kafka consumer started")

    def _consume_loop(self) -> None:
        """
        Main consumer loop.
        """
        while self._running:
            try:
                # Poll for messages
                records = self._consumer.poll(timeout_ms=1000, max_records=10)
                
                for topic_partition, messages in records.items():
                    topic = topic_partition.topic
                    
                    if topic in self._handlers:
                        handler = self._handlers[topic]
                        
                        for message in messages:
                            try:
                                # Process message
                                handler(message.value)
                            except Exception as e:
                                logger.error(f"Error processing message from topic {topic}: {str(e)}")
                    else:
                        logger.warning(f"No handler registered for topic: {topic}")
                        
            except KafkaError as e:
                logger.error(f"Kafka error in consumer loop: {str(e)}")
                time.sleep(1)  # Avoid tight loop in case of errors
            except Exception as e:
                logger.error(f"Unexpected error in consumer loop: {str(e)}")
                time.sleep(1)  # Avoid tight loop in case of errors

    def stop(self) -> None:
        """
        Stop consuming messages from Kafka.
        """
        if not self._running:
            logger.warning("Kafka consumer not running")
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

        if self._consumer:
            self._consumer.close()
            logger.info("Kafka consumer closed")


# Global instance
kafka_task_consumer = KafkaTaskConsumer()
