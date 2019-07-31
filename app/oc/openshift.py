import os

from kubernetes import client, config
from openshift.dynamic import DynamicClient

from core.log import daac_logging

log = daac_logging()
logger = log.get_logger()


class OpenShiftAccess:
    def __init__(self):

        # Check if code is running in OpenShift
        if "OPENSHIFT_BUILD_NAME" in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config()

    def connect(self):
        # Create a client config
        self.k8s_config = client.Configuration()

        """ OCP Dynamic client requires the parameter configuration to be set
            else it will fail to load an in cluster configuration
        """
        self.k8s_client = client.api_client.ApiClient(configuration=self.k8s_config)
        dyn_client = DynamicClient(self.k8s_client)

        return dyn_client
