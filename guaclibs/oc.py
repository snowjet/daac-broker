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

    def _create_service(self, username):

        username = username

        v1_service = self.dyn_client.resources.get(api_version="v1", kind="Service")

        body = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "svc-%s" % (username)},
            "spec": {
                "ports": [{"port": 8080, "protocol": "TCP", "targetPort": 8080}],
                "selector": {"name": "desktop-%s" % (username)},
            },
        }

        v1_service.create(body=body, namespace=self.namespace)

    def _create_desktop(self, username, XRDP_PASSWORD):

        username = username

        XRDP_PASSWORD = XRDP_PASSWORD

        v1_DeploymentConfig = self.dyn_client.resources.get(
            api_version="v1", kind="DeploymentConfig"
        )

        body = {
            "apiVersion": "v1",
            "kind": "DeploymentConfig",
            "metadata": {
                "annotations": {
                    "description": "Defines how to deploy a Desktop as a Container"
                },
                "labels": {"app": "desktop-%s" % (username)},
                "name": "desktop-%s" % (username),
            },
            "spec": {
                "replicas": 1,
                "selector": {"name": "desktop-%s" % (username)},
                "strategy": {"type": "Rolling"},
                "template": {
                    "metadata": {
                        "labels": {"name": "desktop-%s" % (username)},
                        "name": "desktop-%s" % (username),
                    },
                    "spec": {
                        "containers": [
                            {
                                "env": [
                                    {
                                        "name": "XRDP_PASSWORD",
                                        "value": "%s" % (XRDP_PASSWORD),
                                    }
                                ],
                                "image": "gdesk:latest",
                                "imagePullPolicy": "Always",
                                "livenessProbe": {
                                    "initialDelaySeconds": 15,
                                    "periodSeconds": 2,
                                    "tcpSocket": {"port": "rdp"},
                                },
                                "name": "desktop-%s" % (username),
                                "ports": [{"containerPort": 3389, "name": "rdp"}],
                                "readinessProbe": {
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10,
                                    "tcpSocket": {"port": "rdp"},
                                },
                                "resources": {
                                    "limits": {"cpu": "1500m", "memory": "4Gi"},
                                    "requests": {"cpu": "50m", "memory": "512Mi"},
                                    "volumeMounts": [
                                        {"mountPath": "/dev/shm", "name": "dshm"}
                                    ],
                                },
                            }
                        ],
                        "volumes": [{"emptyDir": {"medium": "Memory"}, "name": "dshm"}],
                    },
                },
                "triggers": [
                    {"type": "ConfigChange"},
                    {
                        "imageChangeParams": {
                            "automatic": True,
                            "containerNames": ["desktop-%s" % (username)],
                            "from": {"kind": "ImageStreamTag", "name": "gdesk:latest"},
                        },
                        "type": "ImageChange",
                    },
                ],
            },
        }

        v1_DeploymentConfig.create(body=body, namespace=self.namespace)

    def deploy_user_daac(self, username, password):

        XRDP_PASSWORD = password

        self._create_desktop(username, XRDP_PASSWORD)
        self._create_service(username)

        return True
