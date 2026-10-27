import logging
from django.conf import settings
from kombu import Connection, Exchange, Producer

logger = logging.getLogger(__name__)

def publish_event(event_type: str, payload: dict):
    """
    Publishes an event to the RabbitMQ topic exchange using Celery's Kombu core.
    Replaces Pika with Celery/Kombu.
    """
    try:
        topic_exchange = Exchange(settings.RABBITMQ_EXCHANGE, type='topic', durable=True)
        with Connection(settings.RABBITMQ_URL, connect_timeout=5) as conn:
            with Producer(conn) as producer:
                message = {'event': event_type, 'data': payload}
                producer.publish(
                    message,
                    exchange=topic_exchange,
                    routing_key=event_type,
                    declare=[topic_exchange],
                    serializer='json',
                    delivery_mode=2,
                )
        logger.info(f"[Celery/Kombu] Published {event_type}: {payload.get('username') or payload.get('id')}")
        return True
    except Exception as exc:
        logger.error(f"[Celery/Kombu] Failed to publish {event_type}: {exc}")
        return False
