import os
import sys
import yaml
from kubernetes import client, config
from openshift.dynamic import DynamicClient

class GuacOC():

    def oc_connection(self):

        k8s_client = config.load_incluster_config
        dyn_client = DynamicClient(k8s_client)

        v1_projects = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Project')

        project_list = v1_projects.get()

        for project in project_list.items:
            print(project.metadata.name)
        
        return project_list
