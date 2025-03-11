"""Base generator for Kubernetes resources."""
from typing import Dict, Any, List

class BaseGenerator:
    def __init__(self, namespace: str):
        self.namespace = namespace

    def _convert_ports(self, ports: List[str | Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Docker compose ports to Kubernetes container ports.
        
        Handles:
        - String format ('80:80')
        - URL format ('http://domain:8080')
        - Dictionary format ({'port': 80, 'protocol': 'http'})
        - Domain format ('domain.com': {'port': 80, 'protocol': 'http'})
        - New expose format ([{'domain.com': {'port': 80, 'protocol': 'http'}}])
        """
        container_ports = []
        for port in ports:
            try:
                if isinstance(port, str):
                    if port.startswith('http'):
                        # Handle URL format (from expose)
                        from urllib.parse import urlparse
                        parsed = urlparse(port)
                        if ':' in parsed.netloc:
                            port = parsed.netloc.split(':')[1]
                        else:
                            port = '80' if parsed.scheme == 'http' else '443'
                    
                    # Handle port format (from ports)
                    target = port.split(':')[-1].split('/')[0]
                    container_ports.append({
                        'containerPort': int(target),
                        'protocol': 'TCP'
                    })
                elif isinstance(port, dict):
                    # Handle new expose format
                    for domain, settings in port.items():
                        if isinstance(settings, dict) and 'port' in settings:
                            container_ports.append({
                                'containerPort': int(settings['port']),
                                'protocol': settings.get('protocol', 'TCP').upper()
                            })
                            break  # Only need one port configuration per expose entry
                    # Handle legacy dictionary format
                    if 'port' in port:
                        container_ports.append({
                            'containerPort': int(port['port']),
                            'protocol': port.get('protocol', 'TCP').upper()
                        })
            except Exception:
                continue
        
        return container_ports

    def _convert_service_ports(self, ports: List[str | Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Docker compose ports to Kubernetes service ports.
        
        Handles string format ('80:80') for port mappings.
        """
        service_ports = []
        for port in ports:
            try:
                if isinstance(port, str):
                    source, target = port.split(':')[0:2]
                    target = target.split('/')[0]  # Remove protocol if present
                    source_port = int(source)
                    target_port = int(target)
                    service_ports.append({
                        'name': f'port-{source_port}',
                        'port': source_port,
                        'targetPort': target_port,
                        'protocol': 'TCP'
                    })
                elif isinstance(port, dict):
                    published_port = int(port.get('published', 80))
                    service_ports.append({
                        'name': f'port-{published_port}',
                        'port': published_port,
                        'targetPort': int(port.get('target', 80)),
                        'protocol': port.get('protocol', 'tcp').upper()
                    })
            except Exception:
                continue
        
        return service_ports

    def _convert_environment(self, env: Dict[str, str]) -> List[Dict[str, str]]:
        """Convert Docker compose environment to Kubernetes env vars."""
        return [{'name': k, 'value': str(v)} for k, v in env.items()]

    def _convert_env_from(self, env_from: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert envFrom to Kubernetes envFrom."""
        result = []
        for item in env_from:
            if 'config' in item:
                result.append({
                    'configMapRef': {
                        'name': item['config']['name']
                    }
                })
            elif 'secret' in item:
                result.append({
                    'secretRef': {
                        'name': item['secret']['name']
                    }
                })
        return result
