"""
Kafka stream processor for data streaming.
"""
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaStreamProcessor:
    """
    Kafka stream processor for data streaming.
    """
    _instance = None
    _consumer = None
    _producer = None
    _running = False
    _thread = None
    _processors = {}

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of KafkaStreamProcessor is created.
        """
        if cls._instance is None:
            cls._instance = super(KafkaStreamProcessor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initialize stream processor.
        """
        try:
            # Initialize consumer
            self._consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='stream-processor-group',
            )
            
            # Initialize producer
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
            )
            
            logger.info(f"Kafka stream processor initialized with bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka stream processor: {str(e)}")
            self._consumer = None
            self._producer = None

    def register_processor(
        self,
        source_topic: str,
        target_topic: str,
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a processor function for a specific source topic.
        
        Args:
            source_topic: Source Kafka topic
            target_topic: Target Kafka topic
            processor_func: Function to process messages from source topic
        """
        self._processors[source_topic] = {
            "target_topic": target_topic,
            "processor_func": processor_func
        }
        logger.info(f"Registered processor for topic: {source_topic} -> {target_topic}")

    def start(self, topics: Optional[List[str]] = None) -> None:
        """
        Start processing streams from Kafka.
        
        Args:
            topics: List of topics to subscribe to. If None, subscribes to all registered processors.
        """
        if not self._consumer or not self._producer:
            logger.error("Kafka stream processor not initialized")
            return

        if self._running:
            logger.warning("Kafka stream processor already running")
            return

        # If no topics provided, use all registered processors
        if topics is None:
            topics = list(self._processors.keys())

        if not topics:
            logger.warning("No topics to subscribe to")
            return

        # Subscribe to topics
        self._consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")

        # Start processor thread
        self._running = True
        self._thread = threading.Thread(target=self._process_loop)
        self._thread.daemon = True
        self._thread.start()
        logger.info("Kafka stream processor started")

    def _process_loop(self) -> None:
        """
        Main processing loop.
        """
        while self._running:
            try:
                # Poll for messages
                records = self._consumer.poll(timeout_ms=1000, max_records=10)
                
                for topic_partition, messages in records.items():
                    topic = topic_partition.topic
                    
                    if topic in self._processors:
                        processor_config = self._processors[topic]
                        target_topic = processor_config["target_topic"]
                        processor_func = processor_config["processor_func"]
                        
                        for message in messages:
                            try:
                                # Process message
                                processed_value = processor_func(message.value)
                                
                                # Send processed message to target topic
                                self._producer.send(
                                    topic=target_topic,
                                    value=processed_value,
                                    key=message.key
                                )
                            except Exception as e:
                                logger.error(f"Error processing message from topic {topic}: {str(e)}")
                    else:
                        logger.warning(f"No processor registered for topic: {topic}")
                        
            except KafkaError as e:
                logger.error(f"Kafka error in processor loop: {str(e)}")
                time.sleep(1)  # Avoid tight loop in case of errors
            except Exception as e:
                logger.error(f"Unexpected error in processor loop: {str(e)}")
                time.sleep(1)  # Avoid tight loop in case of errors

    def stop(self) -> None:
        """
        Stop processing streams from Kafka.
        """
        if not self._running:
            logger.warning("Kafka stream processor not running")
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

        if self._consumer:
            self._consumer.close()
        
        if self._producer:
            self._producer.close()
            
        logger.info("Kafka stream processor stopped")


# Global instance
kafka_stream_processor = KafkaStreamProcessor()
