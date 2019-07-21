import logging
import daiquiri


class daac_logging:
    def __init__(self):

        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

    def get_logger(self):

        return self.logger
