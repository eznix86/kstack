"""Validators for kstack compose configuration.

Validates apps and their sidecars using JSON Schema, ensuring proper configuration
and resource references."""

import os
import json
from typing import Dict, Any, Set
from jsonschema import validate, ValidationError
from kubernetes import client
from kubernetes.client.rest import ApiException

class ComposeValidator:
    def __init__(self):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'compose_schema.json')
        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate_compose(self, compose_data: Dict[str, Any], external_configs: Set[str], external_secrets: Set[str]):
        """Validate compose configuration using JSON Schema.

        Args:
            compose_data: The compose configuration to validate
            external_configs: Set of external config names that should exist
            external_secrets: Set of external secret names that should exist

        Raises:
            ValidationError: If the compose configuration is invalid
            ValueError: If referenced external resources don't exist
        """
        try:
            # Validate against JSON schema
            validate(instance=compose_data, schema=self.schema)

            # Additional validation for external resources
            self._validate_external_resources(compose_data, external_configs, external_secrets)

        except ValidationError as e:
            # Convert JSON Schema error to more user-friendly message
            path = ' -> '.join(str(p) for p in e.path)
            message = f"Validation error at '{path}': {e.message}"
            raise ValidationError(message)

    def _validate_external_resources(self, compose_data: Dict[str, Any], external_configs: Set[str], external_secrets: Set[str]):
        """Validate that all referenced external resources exist."""
        apps = compose_data.get('apps', {})
        configs = compose_data.get('configs', {})
        
        for app_name, app_config in apps.items():
            # Check volumesFrom configs
            volumes_from = app_config.get('volumesFrom', [])
            for volume in volumes_from:
                if 'config' in volume:
                    config_name = volume['config'].get('name')
                    if config_name:
                        self._validate_config_reference(config_name, app_name, configs, external_configs)

            # Check envFrom configs and secrets
            env_from = app_config.get('envFrom', [])
            for env in env_from:
                if 'config' in env:
                    config_name = env['config'].get('name')
                    if config_name:
                        self._validate_config_reference(config_name, app_name, configs, external_configs)
                elif 'secret' in env:
                    secret_name = env['secret'].get('name')
                    if secret_name and secret_name not in external_secrets:
                        raise ValueError(
                            f"App '{app_name}' references secret '{secret_name}' "
                            "which is not marked as external"
                        )

            # Check sidecars
            sidecars = app_config.get('sidecars', {})
            for sidecar_name, sidecar_config in sidecars.items():
                # Check sidecar volumesFrom
                volumes_from = sidecar_config.get('volumesFrom', [])
                for volume in volumes_from:
                    if 'config' in volume:
                        config_name = volume['config'].get('name')
                        if config_name:
                            self._validate_config_reference(
                                config_name,
                                app_name,
                                configs,
                                external_configs,
                                sidecar_name
                            )

                # Check sidecar envFrom
                env_from = sidecar_config.get('envFrom', [])
                for env in env_from:
                    if 'config' in env:
                        config_name = env['config'].get('name')
                        if config_name:
                            self._validate_config_reference(
                                config_name,
                                app_name,
                                configs,
                                external_configs,
                                sidecar_name
                            )
                    elif 'secret' in env:
                        secret_name = env['secret'].get('name')
                        if secret_name and secret_name not in external_secrets:
                            raise ValueError(
                                f"Sidecar '{sidecar_name}' in app '{app_name}' references "
                                f"secret '{secret_name}' which is not marked as external"
                            )
                            
    def _validate_config_reference(self, config_name: str, app_name: str, configs: Dict[str, Any],
                                 external_configs: Set[str], sidecar_name: str = None):
        """Validate a config reference.
        
        Args:
            config_name: Name of the referenced config
            app_name: Name of the app referencing the config
            configs: Dictionary of all configs in the compose file
            external_configs: Set of external config names
            sidecar_name: Optional name of the sidecar referencing the config
        """
        # Check if config exists in compose file
        if config_name not in configs:
            prefix = f"Sidecar '{sidecar_name}' in " if sidecar_name else ""
            raise ValueError(
                f"{prefix}App '{app_name}' references config '{config_name}' "
                "which does not exist"
            )
        
        # If config is marked as external, validate it's in external_configs
        if configs[config_name].get('external', False):
            if config_name not in external_configs:
                prefix = f"Sidecar '{sidecar_name}' in " if sidecar_name else ""
                raise ValueError(
                    f"{prefix}App '{app_name}' references config '{config_name}' "
                    "which is marked as external but not found in external configs"
                )

class KubernetesResourceValidator:
    """Validates that referenced Kubernetes resources exist."""
    def __init__(self, namespace: str, core_v1_api: client.CoreV1Api = None):
        self.namespace = namespace
        self.core_v1 = core_v1_api

    def validate_external_resources(self, configs: Set[str], secrets: Set[str]):
        """Validate that external resources exist in Kubernetes.
        
        Args:
            configs: Set of ConfigMap names to validate
            secrets: Set of Secret names to validate
            
        Raises:
            ValueError: If any resource doesn't exist in the cluster
        """
        if not self.core_v1:
            return

        self._validate_configs(configs)
        self._validate_secrets(secrets)

    def _validate_configs(self, configs: Set[str]):
        """Validate that external ConfigMaps exist."""
        for config_name in configs:
            try:
                self.core_v1.read_namespaced_config_map(config_name, self.namespace)
            except ApiException as e:
                if e.status == 404:
                    raise ValueError(
                        f"ConfigMap '{config_name}' not found in namespace '{self.namespace}'"
                    )
                raise

    def _validate_secrets(self, secrets: Set[str]):
        """Validate that external Secrets exist."""
        for secret_name in secrets:
            try:
                self.core_v1.read_namespaced_secret(secret_name, self.namespace)
            except ApiException as e:
                if e.status == 404:
                    raise ValueError(
                        f"Secret '{secret_name}' not found in namespace '{self.namespace}'"
                    )
                raise
