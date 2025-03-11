"""Generator for Kubernetes Deployment resources with sidecar support.

Handles both main app containers and their sidecars, ensuring proper resource sharing
and configuration inheritance."""

from typing import Dict, Any, List
from .base_generator import BaseGenerator
from .volume_generator import VolumeGenerator

class DeploymentGenerator(BaseGenerator):
    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.volume_generator = VolumeGenerator(namespace)

    def generate(self, name: str, config: Dict[str, Any], compose_config: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Generate Kubernetes Deployment and ConfigMap resources with sidecars.
        
        Args:
            name: Name of the app
            config: App configuration
            compose_config: Optional full compose configuration for top-level configs
            
        Returns:
            Dictionary containing 'deployments' and 'configmaps' lists
        """
        resources = {
            'deployments': [],
            'configmaps': []
        }
        
        # Generate ConfigMaps for non-external configs
        if compose_config and 'configs' in compose_config:
            for config_name, config_data in compose_config['configs'].items():
                if not config_data.get('external', False):
                    resources['configmaps'].append({
                        'apiVersion': 'v1',
                        'kind': 'ConfigMap',
                        'metadata': {
                            'name': f"config-{config_name}",
                            'namespace': self.namespace
                        },
                        'data': config_data.get('data', {})
                    })
        
        # Create main container
        main_container = self._create_container(name, config, config)
        containers = [main_container]

        # Add sidecar containers if present
        sidecars = config.get('sidecars', {})
        for sidecar_name, sidecar_config in sidecars.items():
            # Merge inherited configurations
            merged_config = self._merge_sidecar_config(config, sidecar_config)
            # Create sidecar container
            sidecar = self._create_container(f"{name}-{sidecar_name}", merged_config, config)
            containers.append(sidecar)

        # Prepare volumes
        volumes = self.volume_generator.generate_volumes(name, config)

        # Add deployment to resources
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': name,
                'namespace': self.namespace
            },
            'spec': {
                'replicas': config.get('deploy', {}).get('replicas', 1),
                'selector': {
                    'matchLabels': {
                        'app': name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': name
                        }
                    },
                    'spec': {
                        'containers': containers,
                        'volumes': volumes
                    }
                }
            }
        }
        resources['deployments'].append(deployment)
        
        # Return all resources
        return resources

    def _convert_volume_mounts(self, name: str, volumes: List[str]) -> List[Dict[str, Any]]:
        """Convert Docker compose volumes to Kubernetes volume mounts."""
        volume_mounts = []
        for i, volume in enumerate(volumes):
            if isinstance(volume, str):
                parts = volume.split(':')
                if len(parts) >= 2:
                    # Generate the same volume name as in volume_generator
                    volume_name = f"vol-{name}-{i}"
                    volume_mounts.append({
                        'name': volume_name,
                        'mountPath': parts[1]
                    })
        return volume_mounts

    def _create_container(self, name: str, config: Dict[str, Any], app_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a container specification for either main app or sidecar.
        
        Args:
            name: Container name
            config: Container configuration
            app_config: Optional full app configuration for inline config lookup
        """
        container = {
            'name': name,
            'image': config['image'],
            'ports': self._convert_ports(config.get('ports', [])),
            'env': self._convert_environment(config.get('environment', {})),
            'volumeMounts': self._convert_volume_mounts(name, config.get('volumes', []))
        }

        # Add envFrom if specified
        if 'envFrom' in config:
            container['envFrom'] = self._convert_env_from(config['envFrom'])

        # Add volume mounts from configs
        if 'volumesFrom' in config:
            container['volumeMounts'].extend(self._convert_volumes_from(config['volumesFrom'], app_config))

        return container

    def _merge_sidecar_config(self, app_config: Dict[str, Any], sidecar_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge app-level configuration with sidecar configuration.

        Inherits certain configurations from the main app while allowing sidecar overrides.
        """
        merged = sidecar_config.copy()

        # Inherit these fields from the main app if not specified in sidecar
        inheritable_fields = ['volumes', 'networks', 'env_file', 'volumesFrom']
        for field in inheritable_fields:
            if field in app_config and field not in merged:
                merged[field] = app_config[field]

        return merged

    def _convert_volumes_from(self, volumes_from: List[Dict[str, Any]], app_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Convert volumesFrom to volume mounts.
        
        Args:
            volumes_from: List of volume configurations
            app_config: Optional app configuration to check for inline configs
        """
        volume_mounts = []
        for volume in volumes_from:
            if 'config' in volume:
                config_name = volume['config']['name']
                volume_mounts.append({
                    'name': f"config-{config_name}",
                    'mountPath': volume.get('mountPath', f"/config/{config_name}")
                })
        return volume_mounts
