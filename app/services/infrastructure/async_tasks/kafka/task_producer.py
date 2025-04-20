"""
Kafka task producer for async tasks.
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.infrastructure.kafka.producer import BaseKafkaProducer

logger = logging.getLogger(__name__)


class TaskProducer(BaseKafkaProducer):
    """
    Kafka producer for sending task messages.
    """
    
    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Submit a task to be processed asynchronously.
        
        Args:
            task_type: Type of task to execute
            payload: Task data
            user_id: ID of the user who submitted the task
            task_id: Custom task ID (if not provided, a UUID will be generated)
            
        Returns:
            Task ID
        """
        # Generate task ID if not provided
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Create task message
        message = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "pending",
            "payload": payload,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Send task to Kafka
        success = self.send(
            topic_key="async_tasks",
            value=message,
            key=task_id
        )
        
        if not success:
            logger.error(f"Failed to submit task {task_id}")
        
        return task_id


# Global instance
task_producer = TaskProducer()
