"""
Opentelemetry implementations
"""
import os
import logging
from contextlib import contextmanager
from opentracing import global_tracer, set_global_tracer
from opentelemetry.trace import set_tracer_provider, get_tracer_provider, get_tracer
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.shim.opentracing_shim import create_tracer
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

LOGGER = logging.getLogger(__name__)


def traced(span_name: str):
    """
    decorator for tracing a function, allows providing a name (span_name)

    :param span_name: name for the trace span
    :type span_name: str
    :return:
    :rtype: callable
    """
    def _decorator(func):
        def _wrapper(*args, **kwargs):
            @contextmanager
            def _start_active_span():
                if os.environ.get('OPENTRACING_MODE'):
                    with global_tracer().start_active_span(f'opentracing_{span_name}'):
                        yield
                else:
                    with get_tracer(__name__).start_as_current_span(f'otel_{span_name}'):
                        yield

            with _start_active_span():
                return func(*args, **kwargs)
        return _wrapper
    return _decorator


def bootstrap_tracer(service_name: str):
    LOGGER.info('Bootstrapping opentelemetry tracer')
    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            DEPLOYMENT_ENVIRONMENT: "local"
        }
    )
    exporter = OTLPSpanExporter(
        endpoint=os.environ['OTLP_ENDPOINT'],
        insecure=True,
    )

    span_processor = BatchSpanProcessor(exporter)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    set_tracer_provider(provider)
    LOGGER.info('otel tracer setup')

    shim = create_tracer(get_tracer_provider())
    set_global_tracer(shim)
    LOGGER.info('opentracing tracer setup')
