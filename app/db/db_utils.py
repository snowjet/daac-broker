import hashlib
import os
import uuid

from app.core.log import logger
from app.db.database import DataBase

logger.info("Get DB instance")
db = DataBase()
