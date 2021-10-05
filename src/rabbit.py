from contextlib import contextmanager
import logging
import pika

LOGGER = logging.getLogger(__name__)


def get_rabbit_connection():
    credentials = pika.PlainCredentials(
        'guest',
        'guest'
    )
    parameters = pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        virtual_host='/',
        heartbeat=30,
        credentials=credentials,
        connection_attempts=20,
        retry_delay=3
    )
    return pika.BlockingConnection(parameters=parameters)


@contextmanager
def rabbit_context():
    """
    """
    try:
        yield get_rabbit_connection()
    except (pika.exceptions.ChannelClosed, pika.exceptions.ConnectionClosed) as conn_err:
        LOGGER.warning('RabbitMQ connection problem: %s, will attempt to reconnect on next use', conn_err)
    except pika.exceptions.AMQPError as amqp_err:
        LOGGER.warning('AMQP error: %s, will attempt to reconnect on next use', amqp_err)
        LOGGER.exception(amqp_err)


def setup_queue():
    with rabbit_context() as conn:
        chan = conn.channel()
        chan.exchange_declare(exchange='test', exchange_type='topic', durable=True)
        chan.queue_declare(queue='test_q', durable=True)
        chan.queue_bind(queue='test_q', exchange='test', routing_key='otel.sink')


def add_rabbit_trace_tags(span, message_id, destination):
    """
    Given an active span, add standard opentracing message bus tags for RabbitMQ

    @see: https://opentracing.io/docs/best-practices/

    @see: https://github.com/opentracing/specification/blob/master/semantic_conventions.md#message-bus

    :param span:
    :type span:
    :param message_id:
    :type message_id: str
    :param destination: dict of exchange and routing_key
    :type destination: dict[str, str]
    :return: span
    :rtype:
    """
    span.set_tag('messaging.system', 'rabbitmq')
    span.set_tag('messaging.protocol', 'AMQP')
    span.set_tag('messaging.destination', destination['exchange'])
    span.set_tag('messaging.rabbitmq.routing_key', destination['routing_key'])
    span.set_tag('message_bus.message_id', message_id)
    span.set_tag('messaging.message_id', message_id)

    return span
