"""
Opentelemetry implementations
"""
import os
import logging
from contextlib import contextmanager
from jaeger_client import Config
from opentracing import global_tracer, set_global_tracer
from opentelemetry.trace import set_tracer_provider, get_tracer_provider, get_tracer
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.shim.opentracing_shim import create_tracer
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

LOGGER = logging.getLogger(__name__)


def bootsrap_jaeger(service_name: str):
    cfg = {
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    }
    config = Config(cfg, service_name=service_name)
    config.initialize_tracer()


def bootstrap_tracer(service_name: str):
    if os.environ.get('JAEGER_MODE'):
        bootsrap_jaeger(service_name)
        return

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
