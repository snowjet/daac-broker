from core.log import logger
from oc.openshift import OpenShiftAccess

logger.info("Get OpenShift Connection")
oc = OpenShiftAccess()
oc_conn = oc.connect()


def get_oc_connection():
    return oc_conn
