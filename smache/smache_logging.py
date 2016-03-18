import logging
import sys

logger = logging.getLogger('smache')


def setup_logger(options):
    if options.debug:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
