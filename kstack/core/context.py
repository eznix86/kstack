"""Kubernetes context management."""
import os
import logging
from kubernetes import client, config
from kubernetes.config import ConfigException
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesContext:
    @staticmethod
    def validate_connection():
        """Validate connection to Kubernetes cluster and get current context."""
        try:
            # Load kube config
            try:
                config.load_kube_config()
                logger.debug("Loaded config from default location")
            except ConfigException:
                # Try loading from KUBECONFIG env var
                kubeconfig = os.getenv('KUBECONFIG')
                if not kubeconfig:
                    raise Exception(
                        "Could not find Kubernetes configuration. "
                        "Please set KUBECONFIG environment variable or ensure ~/.kube/config exists."
                    )
                try:
                    config.load_kube_config(config_file=kubeconfig)
                    logger.debug(f"Loaded config from KUBECONFIG: {kubeconfig}")
                except ConfigException as e:
                    raise Exception(
                        f"Could not load Kubernetes configuration from {kubeconfig}. "
                        "Please check if the file exists and has correct permissions."
                    ) from e
            
            try:
                # Get current context
                _, active_context = config.list_kube_config_contexts()
                logger.debug(f"Active context: {active_context}")
            except Exception as e:
                raise Exception(
                    "Could not get current Kubernetes context. "
                    "Please check if your kubeconfig has a valid current-context."
                ) from e
            
            # Get cluster info
            v1 = client.CoreV1Api()
            try:
                logger.debug(f"Attempting to connect to cluster at {client.Configuration().host}")
                response = v1.list_namespace(limit=1)
                logger.debug(f"Successfully connected to cluster, found {len(response.items)} namespaces")
            except ApiException as e:
                if e.status == 401:
                    logger.error(f"Authentication failed: {e}")
                    raise Exception(
                        "Authentication failed. "
                        "Please check your credentials and ensure you have access to the cluster."
                    ) from e
                elif e.status == 403:
                    logger.error(f"Permission denied: {e}")
                    raise Exception(
                        "Permission denied. "
                        "Please check if you have the necessary permissions to list namespaces."
                    ) from e
                else:
                    logger.error(f"API Exception: {e}")
                    raise Exception(
                        f"Could not connect to Kubernetes cluster: {e.reason}. "
                        "Please check if the cluster is running and accessible."
                    ) from e
            except Exception as e:
                logger.error(f"Connection error: {e}")
                raise Exception(
                    "Could not connect to Kubernetes cluster. "
                    "Please check if the cluster is running and accessible."
                ) from e
            
            return {
                'context': active_context['name'],
                'cluster': active_context['context']['cluster'],
                'server': active_context['context'].get('server', 'unknown'),
                'namespace': active_context['context'].get('namespace', 'default')
            }
            
        except Exception as e:
            if isinstance(e, Exception) and e.__cause__:
                logger.error(f"Connection validation failed: {e}", exc_info=True)
                raise e
            logger.error("Connection validation failed", exc_info=True)
            raise Exception(
                "Could not validate Kubernetes connection. "
                "Please check your kubeconfig file or KUBECONFIG environment variable."
            ) from e
