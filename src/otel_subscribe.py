import logging
from functools import wraps
from opentracing import global_tracer, Format, follows_from, tags
from src.logs import setup_logging
from src.rabbit import rabbit_context, add_rabbit_trace_tags, setup_queue
from src.otel_impl import bootstrap_tracer

LOGGER = logging.getLogger(__name__)


def traced_subscriber(callback):
    """
    Decorator for adding opentracing capabilities to RabbitMQ message subscriber callback.

    @see: https://opentracing.io/docs/best-practices/

    @see: https://github.com/opentracing/specification/blob/master/semantic_conventions.md#message-bus

    :param callback:
    :type callback: callable
    :rtype: callable
    """
    @wraps(callback)
    def trace_callback(*args, **kwargs):
        """
        Wrapper for tracing rabbitMQ message subscriber callback

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        tracer = global_tracer()
        cargs = []
        if len(args) > 4:
            # handle self
            cargs.append(args[0])
            args = args[1:]

        channel, method, properties, body = args
        properties.headers = properties.headers or {}
        transmitted_context = tracer.extract(Format.TEXT_MAP, properties.headers)
        if not transmitted_context and B3Codec:  # pragma: no cover
            # use b3 codec directly to try pulling zipkin headers, if we were not able to pull jaeger ones
            transmitted_context = B3Codec().extract(properties.headers)
        cargs.extend([channel, method, properties, body])
        reference = follows_from(transmitted_context)
        with tracer.start_active_span('message_subscriber', references=[reference]) as scope:
            LOGGER.debug('Starting new opentracing span for message subscriber: %s', scope.span)
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_CONSUMER)

            add_rabbit_trace_tags(
                scope.span,
                properties.message_id,
                {'exchange': method.exchange, 'routing_key': method.routing_key}
            )

            return callback(*cargs, **kwargs)
    return trace_callback


@traced_subscriber
def on_message(channel, method, properties, body):
    LOGGER.info('Here is the content:')
    LOGGER.info(body)
    LOGGER.info(properties)
    channel.basic_ack(delivery_tag=method.delivery_tag)
    return True


def subscribe():
    LOGGER.info('Setup queue')
    setup_queue()
    LOGGER.info('Starting subscription loop')
    while True:
        with rabbit_context() as conn:
            chan = conn.channel()
            chan.basic_qos(prefetch_count=1)
            chan.basic_consume(
                queue='test_q',
                on_message_callback=on_message,
                consumer_tag='otel_subscriber'
            )
            chan.start_consuming()


if __name__ == '__main__':
    setup_logging()
    bootstrap_tracer('otel.subscriber')
    subscribe()
