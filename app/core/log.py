import logging
import daiquiri

from app.core.config import LOG_LEVEL


class daac_logging:
    def __init__(self):

        daiquiri.setup(level=LOG_LEVEL)
        self.logger = daiquiri.getLogger(__name__)

    def get_logger(self):

        return self.logger


daiquiri.setup(level=LOG_LEVEL)
logger = daiquiri.getLogger(__name__)
