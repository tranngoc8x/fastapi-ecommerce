"""
API routes for testing Kafka integration.
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies.auth import get_current_admin_user
from app.core.config import settings
from app.services.infrastructure.messaging.kafka.event_producer import event_producer
from app.models.user import User

router = APIRouter()


class KafkaMessage(BaseModel):
    """Schema for Kafka test message."""
    topic: str
    key: str
    value: Dict[str, Any]


@router.post("/send")
async def send_kafka_message(
    *,
    message: KafkaMessage,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Send a test message to Kafka.

    This endpoint allows sending a test message to a specified Kafka topic.
    Only admin users can access this endpoint.

    Args:
        message: The message to send

    Returns:
        JSON with success status
    """
    try:
        success = event_producer.send(
            topic_key=message.topic,
            value=message.value,
            key=message.key
        )

        if success:
            return {
                "status": "success",
                "message": f"Message sent to topic {message.topic}",
                "details": {
                    "topic": message.topic,
                    "key": message.key
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message to Kafka"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message to Kafka: {str(e)}"
        )


@router.get("/topics")
async def get_kafka_topics(
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get available Kafka topics.

    This endpoint returns the configured Kafka topics.
    Only admin users can access this endpoint.

    Returns:
        JSON with topic information
    """
    return {
        "topics": {
            "product_topic": settings.KAFKA_PRODUCT_TOPIC,
            "order_topic": settings.KAFKA_ORDER_TOPIC,
            "user_topic": settings.KAFKA_USER_TOPIC
        },
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS
    }
