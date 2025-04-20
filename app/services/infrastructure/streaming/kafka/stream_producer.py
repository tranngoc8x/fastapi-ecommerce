"""
Kafka stream producer for data streaming.
"""
import logging
from typing import Any, Dict, Optional

from app.services.infrastructure.kafka.producer import BaseKafkaProducer

logger = logging.getLogger(__name__)


class StreamProducer(BaseKafkaProducer):
    """
    Kafka producer for sending stream data.
    """
    
    def send_stream_data(
        self,
        data: Dict[str, Any],
        stream_id: Optional[str] = None,
        partition_key: Optional[str] = None
    ) -> bool:
        """
        Send data to the stream.
        
        Args:
            data: Stream data
            stream_id: Stream identifier
            partition_key: Key for partitioning
            
        Returns:
            True if data was sent successfully, False otherwise
        """
        try:
            # Generate key if partition_key provided
            key = partition_key or stream_id
            
            # Send data
            return self.send(
                topic_key="stream_input",
                value=data,
                key=key
            )
        except Exception as e:
            logger.error(f"Failed to send stream data: {str(e)}")
            return False


# Global instance
stream_producer = StreamProducer()
