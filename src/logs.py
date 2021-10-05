import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)5.5s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
