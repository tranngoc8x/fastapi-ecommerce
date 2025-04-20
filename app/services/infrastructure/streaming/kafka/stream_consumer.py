"""
Kafka stream consumer for data streaming.
"""
import logging
from typing import Any, Callable, Dict, Optional

from app.services.infrastructure.kafka.consumer import BaseKafkaConsumer
from app.services.infrastructure.kafka.producer import BaseKafkaProducer

logger = logging.getLogger(__name__)


class StreamConsumer(BaseKafkaConsumer):
    """
    Kafka consumer for processing stream data.
    """
    
    def __init__(
        self,
        group_id: str = "stream-consumer-group",
        output_producer: Optional[BaseKafkaProducer] = None,
        **config_overrides
    ):
        """
        Initialize stream consumer.
        
        Args:
            group_id: Consumer group ID
            output_producer: Producer for sending processed data
            **config_overrides: Configuration overrides
        """
        super().__init__(group_id=group_id, **config_overrides)
        self._processors = {}
        self._output_producer = output_producer or BaseKafkaProducer()
    
    def register_processor(
        self,
        processor_id: str,
        processor: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a data processor.
        
        Args:
            processor_id: Processor identifier
            processor: Function to process stream data
        """
        self._processors[processor_id] = processor
        logger.info(f"Registered processor: {processor_id}")
        
        # Ensure we have a handler for the stream_input topic
        if not self._handlers:
            self.register_handler(
                topic_key="stream_input",
                handler=self._handle_stream_data
            )
    
    def _handle_stream_data(self, data: Dict[str, Any]) -> None:
        """
        Handle stream data.
        
        Args:
            data: Stream data
        """
        # Process data with all registered processors
        for processor_id, processor in self._processors.items():
            try:
                # Process data
                processed_data = processor(data)
                
                # Send processed data to output topic
                if processed_data:
                    self._output_producer.send(
                        topic_key="stream_output",
                        value=processed_data,
                        key=processor_id
                    )
            except Exception as e:
                logger.error(f"Error processing stream data with processor {processor_id}: {str(e)}")


# Global instance
stream_consumer = StreamConsumer()
