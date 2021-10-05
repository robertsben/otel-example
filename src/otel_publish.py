import logging
import time
import uuid
from functools import wraps
from opentracing import global_tracer, Format, tags
import pika
from src.rabbit import add_rabbit_trace_tags, rabbit_context
from src.logs import setup_logging
from src.otel_impl import bootstrap_tracer

LOGGER = logging.getLogger(__name__)


def traced_publisher(func):
    """
    Decorator for adding opentracing pub/sub functionality to message publisher

    @see: https://opentracing.io/docs/best-practices/

    @see: https://github.com/opentracing/specification/blob/master/semantic_conventions.md#message-bus

    :param func:
    :type func: callable
    :rtype: callable
    """
    @wraps(func)
    def trace_callback(message):
        """
        Wrapper for publish_to function
        """
        tracer = global_tracer()
        with tracer.start_active_span('message_publisher') as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_PRODUCER)

            add_rabbit_trace_tags(
                scope.span,
                message['message_id'],
                {'exchange': 'test', 'routing_key': 'otel.sink'}
            )

            tracer.inject(tracer.active_span, Format.TEXT_MAP, message['headers'])
            LOGGER.debug('Injecting opentracing span context into published message headers: %s', message['headers'])
            return func(message)
    return trace_callback


@traced_publisher
def publish(message):
    properties = pika.BasicProperties(
        message_id=message['message_id'],
        content_type='application/json',
        content_encoding='utf8',
        headers=message['headers'],
        timestamp=int(time.time()),
        delivery_mode=1,  # non-persistent (not written to disk)
    )
    for _ in range(10):
        with rabbit_context() as conn:
            chan = conn.channel()
            chan.basic_publish(
                'test',
                'otel.sink',
                message['body'],
                mandatory=True,
                properties=properties
            )
            return True


if __name__ == '__main__':
    setup_logging()
    bootstrap_tracer('otel.publisher')
    LOGGER.info('just waiting for 5 seconds')
    time.sleep(5)
    msg = {
        'message_id': str(uuid.uuid4()),
        'headers': {},
        'body': '''{"hello": "world!"}'''
    }
    with global_tracer().start_active_span('start'):
        publish(msg)

    LOGGER.info('Sleeping to ensure any remaining traces are exported')
    time.sleep(60)
    LOGGER.info('Dying')
