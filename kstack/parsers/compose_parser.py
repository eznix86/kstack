"""Parser for kstack compose configuration.

Handles the kstack compose format which uses 'apps' instead of 'services' and supports sidecars."""

import yaml
from typing import Dict, Any, Set
from kubernetes import client, config
from .validators import ComposeValidator, KubernetesResourceValidator

class ComposeParser:
    def __init__(self, compose_file: str, namespace: str = 'default', skip_k8s_check: bool = False):
        self.compose_file = compose_file
        self.namespace = namespace
        self.skip_k8s_check = skip_k8s_check
        
        if not skip_k8s_check:
            try:
                config.load_kube_config()
                self.core_v1 = client.CoreV1Api()
            except Exception:
                self.core_v1 = None
        else:
            self.core_v1 = None

        self.k8s_validator = KubernetesResourceValidator(namespace, self.core_v1)
        self.compose_validator = ComposeValidator()
        
    def parse(self) -> Dict[str, Any]:
        """Parse the compose file and return a dictionary of apps and their configurations."""
        compose_data = self._load_compose_file()
        
        # Extract main components
        configs = compose_data.get('configs', {})
        secrets = compose_data.get('secrets', {})
        apps = compose_data.get('apps', {})
        volumes = compose_data.get('volumes', {})
        
        # Get external resources
        external_configs = self._get_external_configs(configs)
        external_secrets = self._get_external_secrets(secrets)
        
        # Process app configs to determine which ones are referenced
        referenced_configs = self._get_referenced_configs(apps)
        
        # Validate compose file structure and contents
        self.compose_validator.validate_compose(
            compose_data,
            external_configs,
            external_secrets
        )
        
        # Only validate external configs that are actually referenced
        external_configs_to_validate = external_configs & referenced_configs
        
        # Validate external resources exist in kubernetes
        if self.core_v1 and not self.skip_k8s_check:
            self.k8s_validator.validate_external_resources(external_configs_to_validate, external_secrets)
        
        return {
            'apps': apps,
            'volumes': volumes,
            'configs': configs,
            'secrets': secrets
        }

    def _load_compose_file(self) -> Dict[str, Any]:
        """Load and parse the compose file."""
        with open(self.compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)
            
        if not isinstance(compose_data, dict):
            raise ValueError("Invalid compose file format")
            
        return compose_data

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

    @staticmethod
    def _get_external_configs(configs: Dict[str, Any]) -> Set[str]:
        """Get names of external configs."""
        return {name for name, config in configs.items() if config.get('external', False)}
    
    @staticmethod
    def _get_external_secrets(secrets: Dict[str, Any]) -> Set[str]:
        """Get names of external secrets."""
        return {name for name, secret in secrets.items() if secret.get('external', False)}
    
    def _get_referenced_configs(self, apps: Dict[str, Any]) -> Set[str]:
        """Get names of configs referenced by apps and their sidecars."""
        referenced_configs = set()
        
        for app_name, app_config in apps.items():
            # Check main app volumesFrom
            if 'volumesFrom' in app_config:
                for volume in app_config['volumesFrom']:
                    if 'config' in volume:
                        referenced_configs.add(volume['config']['name'])
            
            # Check sidecar volumesFrom
            sidecars = app_config.get('sidecars', {})
            for sidecar_name, sidecar_config in sidecars.items():
                if 'volumesFrom' in sidecar_config:
                    for volume in sidecar_config['volumesFrom']:
                        if 'config' in volume:
                            referenced_configs.add(volume['config']['name'])
        
        return referenced_configs
