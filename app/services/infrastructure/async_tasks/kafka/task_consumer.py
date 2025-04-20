"""
Kafka task consumer for async tasks.
"""
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from app.services.infrastructure.kafka.consumer import BaseKafkaConsumer
from app.services.infrastructure.kafka.producer import BaseKafkaProducer

logger = logging.getLogger(__name__)


class TaskConsumer(BaseKafkaConsumer):
    """
    Kafka consumer for processing async tasks.
    """
    
    def __init__(
        self,
        group_id: str = "task-consumer-group",
        result_producer: Optional[BaseKafkaProducer] = None,
        **config_overrides
    ):
        """
        Initialize task consumer.
        
        Args:
            group_id: Consumer group ID
            result_producer: Producer for sending task results
            **config_overrides: Configuration overrides
        """
        super().__init__(group_id=group_id, **config_overrides)
        self._task_handlers = {}
        self._result_producer = result_producer or BaseKafkaProducer()
    
    def register_task_handler(
        self,
        task_type: str,
        handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Register a handler for a specific task type.
        
        Args:
            task_type: Type of task to handle
            handler: Function to handle tasks of this type
        """
        self._task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
        
        # Ensure we have a handler for the async_tasks topic
        if not self._handlers:
            self.register_handler(
                topic_key="async_tasks",
                handler=self._handle_task_message
            )
    
    def _handle_task_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a task message.
        
        Args:
            message: Task message
        """
        task_id = message.get("task_id")
        task_type = message.get("task_type")
        
        if not task_id or not task_type:
            logger.warning("Received task message without task_id or task_type")
            return
        
        # Find handler for this task type
        handler = self._task_handlers.get(task_type)
        
        if not handler:
            logger.warning(f"No handler registered for task type: {task_type}")
            self._send_task_result(task_id, "failed", error="No handler registered for this task type")
            return
        
        try:
            # Update task status to started
            self._send_task_status(task_id, "started")
            
            # Execute task
            payload = message.get("payload", {})
            result = handler(payload)
            
            # Send task result
            self._send_task_result(task_id, "completed", result=result)
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            self._send_task_result(task_id, "failed", error=str(e))
    
    def _send_task_status(self, task_id: str, status: str) -> None:
        """
        Send task status update.
        
        Args:
            task_id: Task ID
            status: Task status
        """
        message = {
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self._result_producer.send(
            topic_key="task_results",
            value=message,
            key=task_id
        )
    
    def _send_task_result(
        self,
        task_id: str,
        status: str,
        result: Any = None,
        error: Optional[str] = None
    ) -> None:
        """
        Send task result.
        
        Args:
            task_id: Task ID
            status: Task status
            result: Task result
            error: Error message
        """
        message = {
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if result is not None:
            message["result"] = result
        
        if error is not None:
            message["error"] = error
        
        self._result_producer.send(
            topic_key="task_results",
            value=message,
            key=task_id
        )


# Global instance
task_consumer = TaskConsumer()
