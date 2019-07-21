#!/usr/bin/env python

import base64
import random
import string
import os
import sys
import yaml
import json

sys.path.append("..")


def main():
    print("Starting Yaml Test")

    username = "user01"
    XRDP_PASSWORD = "pass"

    configIn = {
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

    json_body = json.load(configIn)

    print(json_body)

    # configOut = yaml.dump(configIn)
    # print(configOut)


if __name__ == "__main__":
    main()
