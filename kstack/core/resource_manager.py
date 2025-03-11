"""Resource manager for Kubernetes resources."""
from typing import Dict, Any, List
import base64
from kubernetes import client

class ResourceManager:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def create_secret_data(self, from_env_file: str, from_literal: List[str]) -> Dict[str, str]:
        """Create secret data from env file and literal values."""
        data = {}
        
        # Load from env file if provided
        if from_env_file:
            with open(from_env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        data[key.strip()] = base64.b64encode(value.strip().encode()).decode()
        
        # Load from literal values
        for item in from_literal:
            key, value = item.split('=', 1)
            data[key.strip()] = base64.b64encode(value.strip().encode()).decode()
            
        return data

    def create_config_data(self, from_env_file: str, from_literal: List[str]) -> Dict[str, str]:
        """Create ConfigMap data from env file and literal values."""
        data = {}
        
        # Load from env file if provided
        if from_env_file:
            with open(from_env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip()
        
        # Load from literal values
        for item in from_literal:
            key, value = item.split('=', 1)
            data[key.strip()] = value.strip()
            
        return data

    def apply_secret(self, name: str, data: Dict[str, str]):
        """Apply a Kubernetes Secret."""
        secret = client.V1Secret(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            data=data
        )
        self.v1.create_namespaced_secret(namespace=self.namespace, body=secret)

    def apply_config_map(self, name: str, data: Dict[str, str]):
        """Apply a Kubernetes ConfigMap."""
        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            data=data
        )
        self.v1.create_namespaced_config_map(namespace=self.namespace, body=config_map)

    def apply_resources(self, resources: Dict[str, List[Dict[str, Any]]]):
        """Apply Kubernetes resources to the cluster using strategic merge patch."""
        # Apply resources in order: ConfigMaps/Secrets -> PVCs -> Services -> Deployments -> Ingress
        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                name = resource['metadata']['name']
                try:
                    if resource_type == 'configmaps':
                        try:
                            self.v1.read_namespaced_config_map(name=name, namespace=self.namespace)
                            self.v1.patch_namespaced_config_map(
                                name=name,
                                namespace=self.namespace,
                                body=resource,
                                field_manager='kube-composer'
                            )
                        except client.exceptions.ApiException as e:
                            if e.status == 404:
                                self.v1.create_namespaced_config_map(
                                    namespace=self.namespace,
                                    body=resource
                                )
                            else:
                                raise
                    if resource_type == 'pvcs':
                        try:
                            self.v1.read_namespaced_persistent_volume_claim(name=name, namespace=self.namespace)
                            self.v1.patch_namespaced_persistent_volume_claim(
                                name=name,
                                namespace=self.namespace,
                                body=resource,
                                field_manager='kube-composer'
                            )
                        except client.exceptions.ApiException as e:
                            if e.status == 404:
                                self.v1.create_namespaced_persistent_volume_claim(
                                    namespace=self.namespace,
                                    body=resource
                                )
                            else:
                                raise
                    elif resource_type == 'services':
                        try:
                            self.v1.read_namespaced_service(name=name, namespace=self.namespace)
                            self.v1.patch_namespaced_service(
                                name=name,
                                namespace=self.namespace,
                                body=resource,
                                field_manager='kube-composer'
                            )
                        except client.exceptions.ApiException as e:
                            if e.status == 404:
                                self.v1.create_namespaced_service(
                                    namespace=self.namespace,
                                    body=resource
                                )
                            else:
                                raise
                    elif resource_type == 'deployments':
                        try:
                            self.apps_v1.read_namespaced_deployment(name=name, namespace=self.namespace)
                            self.apps_v1.patch_namespaced_deployment(
                                name=name,
                                namespace=self.namespace,
                                body=resource,
                                field_manager='kube-composer'
                            )
                        except client.exceptions.ApiException as e:
                            if e.status == 404:
                                self.apps_v1.create_namespaced_deployment(
                                    namespace=self.namespace,
                                    body=resource
                                )
                            else:
                                raise
                    elif resource_type == 'ingress':
                        try:
                            self.networking_v1.read_namespaced_ingress(name=name, namespace=self.namespace)
                            self.networking_v1.patch_namespaced_ingress(
                                name=name,
                                namespace=self.namespace,
                                body=resource,
                                field_manager='kube-composer'
                            )
                        except client.exceptions.ApiException as e:
                            if e.status == 404:
                                self.networking_v1.create_namespaced_ingress(
                                    namespace=self.namespace,
                                    body=resource
                                )
                            else:
                                raise
                except Exception as e:
                    raise Exception(f"Failed to apply {resource_type} '{name}': {str(e)}") from e

    def delete_resources(self, resources: Dict[str, List[Dict[str, Any]]]):
        """Delete Kubernetes resources from the cluster.
        
        Resources are deleted in reverse order to handle dependencies:
        Ingress -> Deployments -> Services -> ConfigMaps -> PVCs
        """
        # Delete resources in reverse order
        resource_types = ['ingress', 'deployments', 'services', 'configmaps', 'pvcs']
        
        for resource_type in resource_types:
            if resource_type not in resources:
                continue
                
            for resource in resources[resource_type]:
                name = resource['metadata']['name']
                try:
                    if resource_type == 'pvcs':
                        self.v1.delete_namespaced_persistent_volume_claim(
                            name=name,
                            namespace=self.namespace
                        )
                    elif resource_type == 'services':
                        self.v1.delete_namespaced_service(
                            name=name,
                            namespace=self.namespace
                        )
                    elif resource_type == 'deployments':
                        self.apps_v1.delete_namespaced_deployment(
                            name=name,
                            namespace=self.namespace
                        )
                    elif resource_type == 'configmaps':
                        self.v1.delete_namespaced_config_map(
                            name=name,
                            namespace=self.namespace
                        )
                    elif resource_type == 'ingress':
                        self.networking_v1.delete_namespaced_ingress(
                            name=name,
                            namespace=self.namespace
                        )
                except client.exceptions.ApiException as e:
                    if e.status != 404:  # Ignore if resource doesn't exist
                        raise Exception(f"Failed to delete {resource_type} '{name}': {str(e)}") from e
