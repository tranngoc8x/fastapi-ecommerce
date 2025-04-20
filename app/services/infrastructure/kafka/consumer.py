"""
Kafka base consumer module.
"""
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.services.infrastructure.kafka.config import KafkaConfig

logger = logging.getLogger(__name__)


class BaseKafkaConsumer:
    """
    Base Kafka consumer class.
    """
    _instances = {}  # Class-level dictionary to store instances
    
    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern per class (not shared between subclasses).
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(BaseKafkaConsumer, cls).__new__(cls)
            cls._instances[cls]._initialized = False
        return cls._instances[cls]
    
    def __init__(
        self,
        group_id: str,
        value_deserializer: Optional[Callable] = None,
        key_deserializer: Optional[Callable] = None,
        **config_overrides
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            group_id: Consumer group ID
            value_deserializer: Function to deserialize message values
            key_deserializer: Function to deserialize message keys
            **config_overrides: Configuration overrides
        """
        # Only initialize once
        if self._initialized:
            return
            
        self._consumer = None
        self._running = False
        self._thread = None
        self._handlers = {}
        self._topics = set()
        
        # Default deserializers
        if value_deserializer is None:
            value_deserializer = lambda v: json.loads(v.decode('utf-8'))
        
        if key_deserializer is None:
            key_deserializer = lambda k: k.decode('utf-8') if k else None
        
        # Get configuration
        config = KafkaConfig.get_consumer_config(group_id, **config_overrides)
        config["value_deserializer"] = value_deserializer
        config["key_deserializer"] = key_deserializer
        
        self._initialize_consumer(config)
        self._initialized = True
    
    def _initialize_consumer(self, config: Dict[str, Any]) -> None:
        """
        Initialize Kafka consumer with configuration.
        
        Args:
            config: Consumer configuration
        """
        try:
            self._consumer = KafkaConsumer(**config)
            logger.info(f"Kafka consumer initialized with bootstrap servers: {config['bootstrap_servers']}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            self._consumer = None
    
    def register_handler(
        self,
        topic_key: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a handler for a specific topic.
        
        Args:
            topic_key: Topic key (will be resolved to actual topic name)
            handler: Function to handle messages from this topic
        """
        # Resolve topic name
        topic = KafkaConfig.get_topic(topic_key)
        
        self._handlers[topic] = handler
        self._topics.add(topic)
        logger.info(f"Registered handler for topic: {topic}")
    
    def start(self, topics: Optional[List[str]] = None) -> None:
        """
        Start consuming messages from Kafka.
        
        Args:
            topics: List of topic keys to subscribe to. If None, subscribes to all registered handlers.
        """
        if not self._consumer:
            logger.error("Kafka consumer not initialized")
            return
        
        if self._running:
            logger.warning("Kafka consumer already running")
            return
        
        # If topics provided, resolve them
        if topics:
            resolved_topics = [KafkaConfig.get_topic(topic_key) for topic_key in topics]
            self._topics.update(resolved_topics)
        
        if not self._topics:
            logger.warning("No topics to subscribe to")
            return
        
        # Subscribe to topics
        self._consumer.subscribe(list(self._topics))
        logger.info(f"Subscribed to topics: {self._topics}")
        
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
            self._consumer = None
