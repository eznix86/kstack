"""Generator for Kubernetes Ingress resources."""
from typing import Dict, Any, List
from urllib.parse import urlparse
from .base_generator import BaseGenerator

class IngressGenerator(BaseGenerator):
    def generate(self, name: str, config: Dict[str, Any], service: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Kubernetes Ingress resource.
    
        """
        if 'expose' not in config:
            return None

        rules = []
        ingress_class_name = 'traefik'

        for expose in config['expose']:
            try:
                if isinstance(expose, str):
                    # Old format: URL string
                    if not expose.startswith(('http://', 'https://')):
                        continue
                        
                    parsed = urlparse(expose)
                    host = parsed.netloc
                    if ':' in host:  # Remove port if present
                        host = host.split(':')[0]
                    path = parsed.path or '/'
                    scheme = parsed.scheme
                    service_port = 80 if scheme == 'http' else 443
                    
                elif isinstance(expose, dict):
                    # New format: dictionary with domain and settings
                    if not expose:  # Skip empty entries
                        continue
                    
                    # Get the domain and settings
                    for domain, settings in expose.items():
                        if not isinstance(settings, dict):
                            continue
                            
                        host = domain.rstrip(':')  # Remove trailing colon if present
                        scheme = settings.get('protocol', 'http')
                        path = settings.get('path', '/')
                        service_port = settings.get('port', 80)
                        
                        if 'ingressClassName' in settings:
                            ingress_class_name = settings['ingressClassName']
                else:
                    continue

                rules.append({
                    'host': host,
                    'http': {
                        'paths': [{
                            'path': path,
                            'pathType': 'Prefix',
                            'backend': {
                                'service': {
                                    'name': name,
                                    'port': {
                                        'number': service_port
                                    }
                                }
                            }
                        }]
                    }
                })
            except Exception:
                continue

        if not rules:
            return None

        ingress = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': name,
                'namespace': self.namespace
            },
            'spec': {
                'rules': rules
            }
        }

        if ingress_class_name:
            ingress['spec']['ingressClassName'] = ingress_class_name

        return ingress
