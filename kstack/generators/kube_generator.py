"""Main generator for Kubernetes resources with sidecar support.

Handles the generation of all Kubernetes resources from kstack compose files,
including apps and their sidecars."""

from typing import Dict, Any, List
import os
import yaml
from .deployment_generator import DeploymentGenerator
from .service_generator import ServiceGenerator
from .ingress_generator import IngressGenerator
from .volume_generator import VolumeGenerator

class KubeResourceGenerator:
    def __init__(self, compose_config: Dict[str, Any], namespace: str):
        self.config = compose_config
        self.namespace = namespace
        
        # Initialize specialized generators
        self.deployment_generator = DeploymentGenerator(namespace)
        self.service_generator = ServiceGenerator(namespace)
        self.ingress_generator = IngressGenerator(namespace)
        self.volume_generator = VolumeGenerator(namespace)

    def generate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all Kubernetes resources from the compose configuration.
        
        This includes:
        - ConfigMaps for configuration data
        - PVCs for persistent storage
        - Deployments for apps and their sidecars
        - Services for apps and sidecars that expose ports
        - Ingress resources for exposed endpoints
        """
        resources = {
            'configmaps': [], # Generate ConfigMaps first as deployments depend on them
            'pvcs': [],      # Generate PVCs first as deployments depend on them
            'deployments': [],
            'services': [],
            'ingress': []
        }

        # Generate PVCs for volumes first
        for volume_name, volume_config in self.config.get('volumes', {}).items():
            pvc = self.volume_generator.generate_pvc(volume_name, volume_config)
            resources['pvcs'].append(pvc)

        # Generate resources for each app
        for app_name, app_config in self.config['apps'].items():
            # Generate deployment and configmaps
            app_resources = self.deployment_generator.generate(app_name, app_config, self.config)
            resources['deployments'].extend(app_resources['deployments'])
            resources['configmaps'].extend(app_resources['configmaps'])
            
            # Generate services for main app and sidecars
            if self.service_generator.needs_service(app_config):
                services = self.service_generator.generate(app_name, app_config)
                # Handle both single service and list of services
                if isinstance(services, list):
                    resources['services'].extend(services)
                    # Use the main app's ClusterIP service for ingress
                    service_for_ingress = next(
                        (s for s in services if s['metadata'].get('labels', {}).get('component') == 'main'),
                        None
                    )
                else:
                    resources['services'].append(services)
                    service_for_ingress = services

                # Generate ingress if expose is specified
                if 'expose' in app_config and service_for_ingress:
                    ingress = self.ingress_generator.generate(app_name, app_config, service_for_ingress)
                    if ingress:
                        resources['ingress'].append(ingress)

        # Filter out empty lists
        return {k: v for k, v in resources.items() if v}

    def save_to_files(self, resources: Dict[str, List[Dict[str, Any]]], output_dir: str):
        """Save generated resources to YAML files."""
        os.makedirs(output_dir, exist_ok=True)
        
        for resource_type, resource_list in resources.items():
            if resource_list:
                output_file = os.path.join(output_dir, f'{resource_type}.yaml')
                with open(output_file, 'w') as f:
                    yaml.safe_dump_all(resource_list, f)
