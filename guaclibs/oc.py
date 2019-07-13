import os
import sys

import yaml
from kubernetes import client, config
from openshift.dynamic import DynamicClient


class GuacOC:
    def __init__(self):

        # Check if code is running in OpenShift
        if "OPENSHIFT_BUILD_NAME" in os.environ:
            config.load_incluster_config()
            file_namespace = open(
                "/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
            )
            if file_namespace.mode == "r":
                self.namespace = file_namespace.read()
                print(self.namespace)
        else:
            config.load_kube_config()

        # Create a client config
        self.k8s_config = client.Configuration()

        """ OCP Dynamic client requires the parameter configuration to be set
            else it will fail to load an in cluster configuration
        """
        self.k8s_client = client.api_client.ApiClient(configuration=self.k8s_config)
        self.dyn_client = DynamicClient(self.k8s_client)

    def list_projects(self):

        v1_projects = self.dyn_client.resources.get(
            api_version="project.openshift.io/v1", kind="Project"
        )

        project_list = v1_projects.get()

        return project_list

    def list_services(self):

        v1_services = self.dyn_client.resources.get(api_version="v1", kind="Service")

        service_list = v1_services.get(namespace=self.namespace)

        return service_list
