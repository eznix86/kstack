from typing import List

from kstack import dd
from .utils import remove_none


def to_persistent_volume_claim(stack: dict, manifests: List[dict] = []) -> List[dict]:
    for name, spec in stack["volumes"].items():
        manifest = remove_none(
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {"name": f"{name}-pvc"},
                "spec": {
                    "resources": {
                        "requests": {
                            "storage":  spec.get("storage")
                        }
                    },
                    "accessModes": spec.get("access_modes", ["ReadWriteOnce"]),
                    "storageClassName": spec.get('storage_class', None)
                },
            }
        )
        manifests.append(manifest)
    return manifests

        
        

def to_deployments(stack: dict, manifests: List[dict] = []) -> List[dict]:
    for name, app in stack["apps"].items():

        volumes_mounts = {}

        volumes_mounts[name] = []
        
        def container(name: str, spec: dict) -> dict:
            return {
                "name": spec.get("name", name),
                "image": spec.get("image"),
                "ports": [{"containerPort": spec.get("port")}]
                if "port" in spec and spec.get("port")
                else None,
                "volumeMounts": volumes_mounts.get(name),
                "command": spec.get('command', None)
            }

        init_containers = (
            [
                {
                    "name": f"wait-for-{to_wait}",
                    "image": "ghcr.io/groundnuty/k8s-wait-for:v1.6",
                    "imagePullPolicy": "Always",
                    "args": ["pod", f"-lapp={to_wait}"],
                }
                for to_wait in app.get("depends_on")
            ]
            if "depends_on" in app
            else []
        )
            
        volumes = []
        
        for index, attributes in enumerate(app.get('volumes')):
            volume_name = f"volume-{name}-{index}"              

            if isinstance(attributes, str) and attributes.startswith((".", "/")):  
                volumes += [{
                    "name": volume_name,
                    "hostPath": {
                        "path": attributes.split(":")[0],
                        "type": "Directory",
                        "readOnly": "ro" in attributes
                    }
                }]
                
                volumes_mounts[name]+= [{
                    "name": volume_name,
                    "mountPath": attributes.split(":")[1]
                }]
                
            if isinstance(attributes, str) and not attributes.startswith((".", "/")):  
                volumes += [{
                    "name": volume_name,
                    "persistentVolumeClaim": {
                        "claimName": attributes.split(":")[0]+"-pvc"
                    }
                }]
                volumes_mounts[name]+= [{
                    "name": volume_name,
                    "mountPath": attributes.split(":")[1],
                    "readOnly": "ro" in attributes
                }]
                
                
            if isinstance(attributes, dict) and 'directory' in attributes:                
                volumes += [{
                    "name": volume_name,
                    "hostPath": {
                        "path": attributes.get('path'),
                        "type": "DirectoryOrCreate"
                    }
                }]
                
                volumes_mounts[name]+= [{
                    "name": volume_name,
                    "mountPath": attributes.get('mount'),
                    "readOnly": attributes.get('read_only', False)
                }]
                
            if isinstance(attributes, dict) and 'file' in attributes:                
                volumes += [{
                    "name": volume_name,
                    "hostPath": {
                        "path": attributes.get('path'),
                        "type": "FileOrCreate"
                    }
                }]
                
                volumes_mounts[name]+= [{
                    "name": volume_name,
                    "mountPath": attributes.get('mount'),
                    "readOnly": attributes.get('read_only', False)
                }]
                


        sidecars = []
        
        if "sidecars" in app:
            sidecars.extend([
                container(name, sidecar)
                for name, sidecar in app.get("sidecars", {}).items()
            ])

        containers = [container(name, app)] + sidecars

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": app.get("name", name)},
            "spec": {
                "replicas": app.get("deployment", {}).get("replicas", 1),
                "selector": {"matchLabels": {"app": app.get("name", name)}},
                "template": {
                    "metadata": {"labels": {"app": app.get("name", name)}},
                    "spec": {
                        "initContainers": init_containers,
                        "containers": containers,
                        "volumes": volumes
                    },
                },
            },
        }
        manifests.append(remove_none(deployment))

    return manifests


def to_loadbalancers(stack: dict, manifests: List[dict] = []) -> List[dict]:
    for name, app in stack["apps"].items():
        if not app.get("ports") or not all(isinstance(port, str) and ":" in port for port in app.get("ports", [])):
            continue

        loadbalancer = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{app.get('name', name)}-lb"},
            "spec": {
                "selector": {"app": app.get("name", name)},
                "type": "LoadBalancer",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": int(port.split(":")[0]),
                        "targetPort": int(port.split(":")[1]),
                    }
                    for port in app.get("ports", [])
                ],
            },
        }

        manifests.append(remove_none(loadbalancer))
    return manifests


def to_ingresses(stack: dict, manifests: List[dict] = []) -> List[dict]:
    for name, app in stack["apps"].items():
        if not app.get("expose"):
            continue

        expose = app.get("expose")
        for ingress in expose:
            cluster_ip = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": f"{app.get('name', name)}-ingress-svc"},
                "spec": {
                    "selector": {"app": app.get("name", name)},
                    "type": "ClusterIP",
                    "ports": [
                        {
                            "protocol": "TCP",
                            "port": ingress.get("port"),
                            "targetPort": ingress.get("port"),
                        }
                    ],
                },
            }

            manifests.append(remove_none(cluster_ip))

            ingress = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {"name": f"{app.get('name', name)}-ingress"},
                "spec": {
                    "rules": [
                        {
                            "host": str(
                                next(
                                    key
                                    for key, value in dict(ingress).items()
                                    if value is None
                                )
                            ),
                            "http": {
                                "paths": [
                                    {
                                        "path": ingress.get("path", "/"),
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": f"{app.get('name', name)}-ingress-svc",
                                                "port": {
                                                    "number": ingress.get("port", None)
                                                },
                                            }
                                        },
                                    }
                                ],
                            },
                        }
                    ]
                },
            }

            manifests.append(remove_none(ingress))

    return manifests
