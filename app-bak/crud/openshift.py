import openshift

from core.config import NAMESPACE
from core.log import logger
from oc.oc_utils import oc_conn


def list_projects():

    v1_projects = oc_conn.resources.get(
        api_version="project.openshift.io/v1", kind="Project"
    )

    project_list = v1_projects.get()

    return project_list


def list_services():

    v1_services = oc_conn.resources.get(api_version="v1", kind="Service")

    service_list = v1_services.get(namespace=NAMESPACE)

    return service_list


def _create_svc_body(service_name, desktop_name):

    body = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "%s" % (service_name)},
        "spec": {
            "ports": [{"port": 3389, "protocol": "TCP", "targetPort": 3389}],
            "selector": {"name": "%s" % (desktop_name)},
        },
    }

    return body


def _create_desktop_svc(service_name, desktop_name):

    try:

        v1_service = oc_conn.resources.get(api_version="v1", kind="Service")

        service_exists = v1_service.get(namespace=NAMESPACE)

        if any(service_name in item.metadata.name for item in service_exists.items):
            logger.info("Service exists", service=service_name)
            logger.debug("Service exists Dump", DeploymentConfig=service_exists)

            return "SVC already exists skipping"

        else:

            body = _create_svc_body(service_name, desktop_name)

            v1_service.create(body=body, namespace=NAMESPACE)
            logger.info("Service created", service=service_name)

            return "Created SVC %s" % (service_name)

    except openshift.dynamic.exceptions.ConflictError as error_msg:
        logger.warn("Conflict error: Likely resource already exists", error=error_msg)
        pass

    except Exception as error_msg:
        logger.error("Error in API", error=error_msg)


def _create_dc_body(username, desktop_name, password_hash):

    body = {
        "apiVersion": "v1",
        "kind": "DeploymentConfig",
        "metadata": {
            "annotations": {
                "description": "Defines how to deploy a Desktop as a Container"
            },
            "labels": {"app": "%s" % (desktop_name)},
            "name": "%s" % (desktop_name),
        },
        "spec": {
            "replicas": 1,
            "selector": {"name": "%s" % (desktop_name)},
            "strategy": {"type": "Rolling"},
            "template": {
                "metadata": {
                    "labels": {"name": "%s" % (desktop_name)},
                    "name": "%s" % (desktop_name),
                },
                "spec": {
                    "containers": [
                        {
                            "env": [
                                {
                                    "name": "PASSWORD_HASH",
                                    "value": "%s" % (password_hash),
                                },
                                {"name": "USERNAME", "value": "%s" % (username)},
                            ],
                            "image": "gdesk:latest",
                            "imagePullPolicy": "Always",
                            "livenessProbe": {
                                "initialDelaySeconds": 15,
                                "periodSeconds": 2,
                                "tcpSocket": {"port": "rdp"},
                            },
                            "name": "%s" % (desktop_name),
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
                        "containerNames": ["%s" % (desktop_name)],
                        "from": {"kind": "ImageStreamTag", "name": "gdesk:latest"},
                    },
                    "type": "ImageChange",
                },
            ],
        },
    }

    return body


def _create_desktop_dc(username, desktop_name, password_hash):

    try:

        v1_DeploymentConfig = oc_conn.resources.get(
            api_version="v1", kind="DeploymentConfig"
        )

        dc_exists = v1_DeploymentConfig.get(namespace=NAMESPACE)

        if any(desktop_name in item.metadata.name for item in dc_exists.items):
            logger.info("DeploymentConfig exists", DeploymentConfig=desktop_name)
            logger.debug("DeploymentConfig exists Dump", DeploymentConfig=dc_exists)

            return "DC already exists skipping"

        else:

            body = _create_dc_body(desktop_name, password_hash)

            v1_DeploymentConfig.create(body=body, namespace=NAMESPACE)

            logger.info("DeploymentConfig created", DeploymentConfig=desktop_name)
            return "Created DC %s" % (desktop_name)

    except openshift.dynamic.exceptions.ConflictError as error_msg:
        logger.warn("Conflict error: Likely resource already exists", error=error_msg)
        pass

    except Exception as error_msg:
        logger.error("Error Occurred in API", error=error_msg)


def create_user_daac(username, password_hash):

    service_name = "desktop-%s" % (username)
    desktop_name = "desktop-%s" % (username)

    dc_msg = _create_desktop_dc(username, desktop_name, password_hash)
    svc_msg = _create_desktop_svc(service_name, desktop_name)

    return dc_msg, svc_msg


def update_user_daac(username):

    service_name = "desktop-%s" % (username)
    desktop_name = "desktop-%s" % (username)

    # dc_msg = _update_desktop_dc(desktop_name, rdp_password)
    # svc_msg = _update_desktop_svc(service_name, desktop_name)

    return True


def _delete_desktop_dc(username):

    try:

        username = username
        desktop_name = "desktop-%s" % (username)

        v1_DeploymentConfig = oc_conn.resources.get(
            api_version="v1", kind="DeploymentConfig"
        )

        dc_exists = v1_DeploymentConfig.get(name=desktop_name, namespace=NAMESPACE)

        logger.info("Print if dc exists", service=dc_exists)

        v1_DeploymentConfig.delete(name=desktop_name, namespace=NAMESPACE)

    except Exception as error_msg:
        logger.error("Error Occurred starting guac-api", error=error_msg)


def _delete_desktop_svc(username):

    try:

        username = username
        service_name = "desktop-%s" % (username)

        v1_service = oc_conn.resources.get(api_version="v1", kind="Service")

        service_exists = v1_service.get(name=service_name, namespace=NAMESPACE)

        logger.info("Print if service exists", service=service_exists)

        v1_service.delete(name=service_name, namespace=NAMESPACE)

    except Exception as error_msg:
        logger.error("Error Occurred starting guac-api", error=error_msg)


def delete_user_daac(username):

    _delete_desktop_dc(username)
    _delete_desktop_svc(username)

    return True
