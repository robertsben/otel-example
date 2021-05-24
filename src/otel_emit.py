import sys
import time
import logging
from opentelemetry.trace import get_tracer
from src.otel_impl import traced, bootstrap_tracer

LOGGER = logging.getLogger(__name__)
TRACER = get_tracer(__name__)


@traced('wait_one')
def wait_one():
    time.sleep(1)


@traced('wait_many')
def wait_many(count):

    for _ in range(count):
        LOGGER.info('waiting...')
        wait_one()


@traced('say_hello')
def say_hello():
    LOGGER.info(f'Hello {__name__}')


@traced('main')
def main():
    say_hello()
    wait_many(5)
    try:
        wait_many('foo')
    except TypeError:
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    bootstrap_tracer('otel_test_app')
    try:
        main()
    except Exception as err:
        LOGGER.exception(err)
        sys.exit()

    LOGGER.info('complete')

