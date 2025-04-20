"""
Kafka task manager for async tasks.
"""
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.core.config import settings
from app.services.infrastructure.messaging.kafka.client import kafka_client
from app.services.infrastructure.async_tasks.kafka.consumer import kafka_task_consumer

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status for async tasks."""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"


class KafkaTaskManager:
    """
    Task manager for Kafka-based async tasks.
    """
    _instance = None
    _tasks = {}  # Store task status in memory (in production, use Redis or DB)

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of KafkaTaskManager is created.
        """
        if cls._instance is None:
            cls._instance = super(KafkaTaskManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initialize task manager.
        """
        # Register task handlers
        kafka_task_consumer.register_handler(
            topic=settings.KAFKA_TASK_TOPIC,
            handler=self._handle_task_update
        )
        
        # Start consumer
        kafka_task_consumer.start()
        
        logger.info("Kafka task manager initialized")

    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """
        Submit a task to be processed asynchronously.
        
        Args:
            task_type: Type of task to execute
            payload: Task data
            user_id: ID of the user who submitted the task
            
        Returns:
            Task ID
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task message
        message = {
            "task_id": task_id,
            "task_type": task_type,
            "status": TaskStatus.PENDING,
            "payload": payload,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Store task status
        self._tasks[task_id] = message
        
        # Send task to Kafka
        success = kafka_client.send_message(
            topic=settings.KAFKA_TASK_TOPIC,
            value=message,
            key=task_id
        )
        
        if not success:
            logger.error(f"Failed to submit task {task_id}")
            # Update task status
            message["status"] = TaskStatus.FAILURE
            message["error"] = "Failed to submit task to Kafka"
            self._tasks[task_id] = message
        
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status information or None if task not found
        """
        return self._tasks.get(task_id)

    def _handle_task_update(self, message: Dict[str, Any]) -> None:
        """
        Handle task update messages from Kafka.
        
        Args:
            message: Task update message
        """
        task_id = message.get("task_id")
        if not task_id:
            logger.error("Received task update without task_id")
            return
        
        # Update task status
        self._tasks[task_id] = message
        logger.info(f"Updated status for task {task_id}: {message.get('status')}")


# Global instance
kafka_task_manager = KafkaTaskManager()
