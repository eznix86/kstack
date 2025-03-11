"""Generator for Kubernetes Service resources with sidecar support.

Creates appropriate services for both main apps and their sidecars, ensuring proper
network access and service discovery."""

from typing import Dict, Any
from .base_generator import BaseGenerator

class ServiceGenerator(BaseGenerator):
    def generate(self, name: str, config: Dict[str, Any]) -> Dict[str, Any] | list[Dict[str, Any]]:
        """Generate Kubernetes Service resources for apps and sidecars.
        
        Creates three types of services:
        1. Default service (same name as app) - LoadBalancer with first port
        2. -lb service - LoadBalancer with additional ports
        3. -ingress service - ClusterIP for expose configuration
        
        Also creates services for sidecars if they expose ports:
        - ClusterIP service with '{app}-{sidecar}' name
        - LoadBalancer service if sidecar needs external access
        """
        services = []
            
        # 1. Default ClusterIP service (same name as app)
        if config.get('ports'):
            port = self._convert_service_ports(config['ports'])[0]
            services.append({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': name,
                    'namespace': self.namespace,
                    'labels': {
                        'app': name,
                        'component': 'main'
                    }
                },
                'spec': {
                    'type': 'ClusterIP',
                    'ports': [{
                        'name': 'default',
                        'port': port['port'],
                        'targetPort': port['targetPort'],
                        'protocol': port['protocol']
                    }],
                    'selector': {
                        'app': name,
                        'component': 'main'
                    }
                }
            })
            

        
        # Handle sidecar services
        sidecars = config.get('sidecars', {})
        for sidecar_name, sidecar_config in sidecars.items():
            if self.needs_service(sidecar_config):
                sidecar_services = self._generate_sidecar_services(name, sidecar_name, sidecar_config)
                services.extend(sidecar_services)

        # 2. Create LoadBalancer service for additional ports (-lb)
        if config.get('ports') and len(config['ports']) > 1:
            ports = self._convert_service_ports(config['ports'])
            # Use second port for -lb service
            port = ports[1]
            services.append({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': f'{name}-lb',
                    'namespace': self.namespace,
                    'labels': {
                        'app': name,
                        'component': 'main'
                    }
                },
                'spec': {
                    'type': 'LoadBalancer',
                    'ports': [{
                        'name': 'lb-https',  # Unique name for LoadBalancer HTTPS port
                        'port': port['port'],
                        'targetPort': port['targetPort'],
                        'protocol': port['protocol']
                    }],
                    'selector': {
                        'app': name,
                        'component': 'main'
                    }
                }
            })
        
        # 3. Create ClusterIP service for expose (-ingress)
        if config.get('expose'):
            services.append({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': f'{name}-ingress',
                    'namespace': self.namespace,
                    'labels': {
                        'app': name,
                        'component': 'main'
                    }
                },
                'spec': {
                    'type': 'ClusterIP',
                    'ports': [{
                        'name': 'ingress-http',
                        'port': 80,
                        'targetPort': 80,
                        'protocol': 'TCP'
                    }],
                    'selector': {
                        'app': name,
                        'component': 'main'
                    }
                }
            })
        
        return services

    def _generate_sidecar_services(self, app_name: str, sidecar_name: str, config: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Generate services for a sidecar container."""
        services = []
        service_name = f"{app_name}-{sidecar_name}"

        # Create ClusterIP service for sidecar
        if config.get('ports'):
            ports = self._convert_service_ports(config['ports'])
            services.append({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': service_name,
                    'namespace': self.namespace,
                    'labels': {
                        'app': app_name,
                        'component': f'sidecar-{sidecar_name}'
                    }
                },
                'spec': {
                    'type': 'ClusterIP',
                    'ports': [{
                        'name': f'port-{i}',
                        'port': port['port'],
                        'targetPort': port['targetPort'],
                        'protocol': port['protocol']
                    } for i, port in enumerate(ports)],
                    'selector': {
                        'app': app_name,
                        'component': f'sidecar-{sidecar_name}'
                    }
                }
            })

            # Create LoadBalancer service if needed
            if any(self._is_external_port(p) for p in config['ports']):
                services.append({
                    'apiVersion': 'v1',
                    'kind': 'Service',
                    'metadata': {
                        'name': f"{service_name}-lb",
                        'namespace': self.namespace,
                        'labels': {
                            'app': app_name,
                            'component': f'sidecar-{sidecar_name}'
                        }
                    },
                    'spec': {
                        'type': 'LoadBalancer',
                        'ports': [{
                            'name': f'lb-port-{i}',
                            'port': port['port'],
                            'targetPort': port['targetPort'],
                            'protocol': port['protocol']
                        } for i, port in enumerate(ports)],
                        'selector': {
                            'app': app_name,
                            'component': f'sidecar-{sidecar_name}'
                        }
                    }
                })

        return services

    def _is_external_port(self, port: str | Dict[str, Any]) -> bool:
        """Determine if a port configuration needs external access."""
        if isinstance(port, str):
            return ':' in port
        return bool(port.get('published'))

    def needs_service(self, config: Dict[str, Any]) -> bool:
        """Determine if an app or sidecar needs a Kubernetes Service resource."""
        return bool(config.get('ports') or config.get('expose'))
