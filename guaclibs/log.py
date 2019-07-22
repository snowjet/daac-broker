import logging
import daiquiri
import os


class daac_logging:
    def __init__(self):

        LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

        daiquiri.setup(level=LOG_LEVEL)
        self.logger = daiquiri.getLogger(__name__)

    def get_logger(self):

        return self.logger
