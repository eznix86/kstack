from typing import List
from kubernetes import client


def apply_persistent_volume_claims(manifests: List["dict"], namespace: str = "default") -> None:
    v1 = client.CoreV1Api()

    for manifest in manifests:
        if manifest["kind"] == "PersistentVolumeClaim":
            name = manifest["metadata"]["name"]
            try:
                v1.read_namespaced_persistent_volume_claim(name=name, namespace=namespace)
                v1.patch_namespaced_persistent_volume_claim(
                    name=name,
                    namespace=namespace,
                    body=manifest,
                    field_manager="kstack",
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    v1.create_namespaced_persistent_volume_claim(
                        namespace=namespace,
                        body=manifest,
                    )
                else:
                    raise

    return manifests


def apply_deployments(manifests: List["dict"], namespace: str = "default") -> None:
    apps_v1 = client.AppsV1Api()

    for manifest in manifests:
        if manifest["kind"] == "Deployment":
            name = manifest["metadata"]["name"]
            try:
                apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
                apps_v1.patch_namespaced_deployment(
                    name=name,
                    namespace=namespace,
                    body=manifest,
                    field_manager="kstack",
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    apps_v1.create_namespaced_deployment(
                        namespace=namespace,
                        body=manifest,
                    )
                else:
                    raise

    return manifests


def apply_services(manifests: List["dict"], namespace: str = "default") -> None:
    v1 = client.CoreV1Api()

    for manifest in manifests:
        if manifest["kind"] == "Service":
            name = manifest["metadata"]["name"]
            try:
                v1.read_namespaced_service(name=name, namespace=namespace)
                v1.patch_namespaced_service(
                    name=name,
                    namespace=namespace,
                    body=manifest,
                    field_manager="kstack",
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    v1.create_namespaced_service(
                        namespace=namespace,
                        body=manifest,
                    )
                else:
                    raise

    return manifests


def apply_ingresses(manifests: List["dict"], namespace: str = "default") -> None:
    v1 = client.NetworkingV1Api()

    for manifest in manifests:
        if manifest["kind"] == "Ingress":
            name = manifest["metadata"]["name"]
            try:
                v1.read_namespaced_ingress(name=name, namespace=namespace)
                v1.patch_namespaced_ingress(
                    namespace=namespace,
                    name=name,
                    body=manifest,
                    field_manager="kstack",
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    v1.create_namespaced_ingress(
                        namespace=namespace,
                        body=manifest,
                    )
                else:
                    raise

    return manifests
