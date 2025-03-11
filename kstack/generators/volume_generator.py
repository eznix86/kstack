"""Generator for Kubernetes Volume and PVC resources."""
from typing import Dict, Any, List
from .base_generator import BaseGenerator

class VolumeGenerator(BaseGenerator):
    def generate_volumes(self, name: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate volumes for a deployment and its sidecars.
        
        Args:
            name: Name of the app
            config: App configuration including sidecars
            
        Returns:
            List of volume definitions for the deployment
        """
        volumes = []
        
        # Process main app volumes
        volumes.extend(self._generate_container_volumes(name, config))
        
        # Process sidecar volumes
        sidecars = config.get('sidecars', {})
        for sidecar_name, sidecar_config in sidecars.items():
            # Merge inherited volumes from main app
            if 'volumes' in config and 'volumes' not in sidecar_config:
                sidecar_config['volumes'] = config['volumes']
            
            sidecar_volumes = self._generate_container_volumes(f"{name}-{sidecar_name}", sidecar_config)
            volumes.extend(sidecar_volumes)
        
        # Deduplicate volumes by name to avoid conflicts
        seen_names = set()
        unique_volumes = []
        for volume in volumes:
            if volume['name'] not in seen_names:
                seen_names.add(volume['name'])
                unique_volumes.append(volume)
        
        return unique_volumes
    
    def _generate_container_volumes(self, name: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate volumes for a single container (main app or sidecar)."""
        volumes = []
        
        # Add volumes from volumesFrom
        if 'volumesFrom' in config:
            for volume in config['volumesFrom']:
                if 'config' in volume:
                    config_name = volume['config']['name']
                    volumes.append({
                        'name': f"config-{config_name}",
                        'configMap': {
                            'name': f"config-{config_name}"
                        }
                    })
        
        # Add regular volumes
        if 'volumes' in config:
            for i, volume in enumerate(config['volumes']):
                if isinstance(volume, str):
                    parts = volume.split(':')
                    if len(parts) >= 2:
                        host_path = parts[0]
                        mount_path = parts[1]
                        
                        # Generate a unique volume name
                        volume_name = f"vol-{name}-{i}"
                        
                        # If the host path starts with /, treat it as a hostPath volume
                        if host_path.startswith('/'):
                            volumes.append({
                                'name': volume_name,
                                'hostPath': {
                                    'path': host_path,
                                    'type': 'Directory'
                                }
                            })
                        else:
                            # Otherwise treat it as a PVC
                            volumes.append({
                                'name': volume_name,
                                'persistentVolumeClaim': {
                                    'claimName': host_path
                                }
                            })

        return volumes

    def generate_pvc(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Kubernetes PersistentVolumeClaim resource."""
        return {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': name,
                'namespace': self.namespace
            },
            'spec': {
                'accessModes': ['ReadWriteOnce'],
                'resources': {
                    'requests': {
                        'storage': config.get('size', '1Gi')
                    }
                }
            }
        }
