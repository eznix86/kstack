"""Tests for kstack resource generators.

Validates that Kubernetes resources are generated correctly from compose configurations,
including proper handling of apps and their sidecars."""

import pytest
from kstack.generators.deployment_generator import DeploymentGenerator
from kstack.generators.service_generator import ServiceGenerator
from kstack.generators.ingress_generator import IngressGenerator

@pytest.fixture
def app_config():
    """Basic app configuration with sidecars."""
    return {
        'image': 'traefik/whoami:latest',
        'ports': ['8080:80'],
        'expose': [{
            'magic-127-0-0-1.nip.io': {
                'port': 80,
                'protocol': 'http',
                'ingressClassName': 'traefik'
            }
        }],
        'sidecars': {
            'metrics': {
                'image': 'prom/node-exporter:latest',
                'ports': ['9100:9100']
            },
            'logger': {
                'image': 'fluent/fluentd:v1.16',
                'volumesFrom': [
                    {'config': {'name': 'fluentd-config', 'mountPath': '/fluentd/etc'}}
                ],
                'volumes': ['/var/log:/fluentd/log'],
                'environment': {
                    'FLUENTD_CONF': 'custom.conf'
                }
            }
        }
    }

def test_deployment_generation(app_config):
    """Test that deployments are generated correctly."""
    generator = DeploymentGenerator(namespace='default')
    app_name = 'whoami'
    config = app_config
    
    # Create compose config with ConfigMap data
    compose_config = {
        'configs': {
            'fluentd-config': {
                'data': {
                    'fluent.conf': 'test config'
                }
            }
        }
    }
    
    resources = generator.generate(app_name, config, compose_config)
    
    # Validate that we have both deployments and configmaps
    assert 'deployments' in resources
    assert 'configmaps' in resources
    
    # Get the deployment
    deployment = resources['deployments'][0]
    
    # Validate deployment structure
    assert deployment['apiVersion'] == 'apps/v1'
    assert deployment['kind'] == 'Deployment'
    assert deployment['metadata']['name'] == app_name
    
    # Validate pod spec
    pod_spec = deployment['spec']['template']['spec']
    containers = pod_spec['containers']
    
    # Check main container
    main_container = containers[0]
    assert main_container['name'] == app_name
    assert main_container['image'] == config['image']
    assert main_container['ports'][0]['containerPort'] == 80
    
    # Check sidecar containers
    metrics_container = next(c for c in containers if c['name'] == f"{app_name}-metrics")
    assert metrics_container['image'] == config['sidecars']['metrics']['image']
    assert metrics_container['ports'][0]['containerPort'] == 9100
    
    logger_container = next(c for c in containers if c['name'] == f"{app_name}-logger")
    assert logger_container['image'] == config['sidecars']['logger']['image']
    assert logger_container['env'][0]['name'] == 'FLUENTD_CONF'
    assert logger_container['env'][0]['value'] == 'custom.conf'
    assert any(mount['mountPath'] == '/fluentd/log' for mount in logger_container['volumeMounts'])
    
    # Check ConfigMap generation
    if 'volumesFrom' in config['sidecars']['logger']:
        config_name = config['sidecars']['logger']['volumesFrom'][0]['config']['name']
        configmap = next((cm for cm in resources['configmaps'] if cm['metadata']['name'] == f'config-{config_name}'), None)
        assert configmap is not None
        assert configmap['kind'] == 'ConfigMap'
        assert configmap['data']['fluent.conf'] == 'test config'

def test_service_generation(app_config):
    """Test that services are generated correctly."""
    generator = ServiceGenerator(namespace='default')
    app_name = 'whoami'
    config = app_config
    
    services = generator.generate(app_name, config)
    
    # We should get four services:
    # 1. Main ClusterIP service (default)
    # 2. Main Ingress service (for expose)
    # 3. Metrics sidecar ClusterIP service
    # 4. Metrics sidecar LoadBalancer service
    assert len(services) == 4
    
    # Find the main service
    main_service = next(s for s in services if s['metadata']['name'] == app_name)
    
    # Validate main service structure
    assert main_service['apiVersion'] == 'v1'
    assert main_service['kind'] == 'Service'
    assert main_service['metadata']['name'] == app_name
    assert main_service['spec']['type'] == 'ClusterIP'
    
    # Check main service ports
    ports = main_service['spec']['ports']
    assert len(ports) == 1  # Main app port
    
    # Main app port
    main_port = ports[0]
    assert main_port['port'] == 8080  # Original port mapping
    assert main_port['targetPort'] == 80  # Container port
    assert main_port['protocol'] == 'TCP'
    
    # Find the metrics sidecar service
    metrics_service = next(s for s in services if s['metadata']['name'] == f'{app_name}-metrics')
    assert metrics_service['spec']['type'] == 'ClusterIP'
    
    # Check metrics service ports
    metrics_ports = metrics_service['spec']['ports']
    assert len(metrics_ports) == 1
    assert metrics_ports[0]['port'] == 9100
    assert metrics_ports[0]['targetPort'] == 9100
    assert metrics_ports[0]['protocol'] == 'TCP'

def test_ingress_generation(app_config):
    """Test that ingress resources are generated correctly."""
    generator = IngressGenerator(namespace='default')
    app_name = 'whoami'
    config = app_config
    
    # Get main service first for ingress generation
    service_generator = ServiceGenerator(namespace='default')
    services = service_generator.generate(app_name, config)
    ingress_service = next(s for s in services if s['metadata']['name'] == f'{app_name}-ingress')
    
    ingress = generator.generate(app_name, config, ingress_service)
    
    # Validate ingress structure
    assert ingress['apiVersion'] == 'networking.k8s.io/v1'
    assert ingress['kind'] == 'Ingress'
    assert ingress['metadata']['name'] == app_name
    
    # Check ingress class
    assert ingress['spec']['ingressClassName'] == 'traefik'
    
    # Check rules
    rules = ingress['spec']['rules']
    assert len(rules) == 1
    
    rule = rules[0]
    assert rule['host'] == 'magic-127-0-0-1.nip.io'
    assert rule['http']['paths'][0]['path'] == '/'
    assert rule['http']['paths'][0]['pathType'] == 'Prefix'
    assert rule['http']['paths'][0]['backend']['service']['name'] == app_name
    assert rule['http']['paths'][0]['backend']['service']['port']['number'] == 80

def test_deployment_with_volume_mounts(app_config):
    """Test that volume mounts are generated correctly."""
    config = app_config.copy()
    config['volumes'] = ['/host/path:/container/path']
    
    # Remove any existing volumes from sidecars to test inheritance
    for sidecar in config['sidecars'].values():
        if 'volumes' in sidecar:
            del sidecar['volumes']
    
    generator = DeploymentGenerator(namespace='default')
    resources = generator.generate('whoami', config)
    
    # Get the deployment
    deployment = resources['deployments'][0]
    
    # Check volume mounts in main container
    main_container = deployment['spec']['template']['spec']['containers'][0]
    assert any(mount['mountPath'] == '/container/path' for mount in main_container.get('volumeMounts', []))
    
    # Check volume mounts in sidecar containers
    metrics_container = next(c for c in deployment['spec']['template']['spec']['containers'] if c['name'] == 'whoami-metrics')
    logger_container = next(c for c in deployment['spec']['template']['spec']['containers'] if c['name'] == 'whoami-logger')
    
    # Verify that sidecars inherit volumes from main app
    assert any(mount['mountPath'] == '/container/path' for mount in metrics_container.get('volumeMounts', []))
    assert any(mount['mountPath'] == '/container/path' for mount in logger_container.get('volumeMounts', []))
    
    # Check volume definitions
    volumes = deployment['spec']['template']['spec']['volumes']
    host_path_volume = next((v for v in volumes if 'hostPath' in v), None)
    assert host_path_volume is not None
    assert host_path_volume['hostPath']['path'] == '/host/path'
    
    # Verify that volume names are unique and consistent
    volume_names = [v['name'] for v in volumes]
    assert len(volume_names) == len(set(volume_names)), 'Volume names must be unique'
    
    # Verify that all volume mounts reference existing volumes
    all_mounts = []
    for container in deployment['spec']['template']['spec']['containers']:
        all_mounts.extend(container.get('volumeMounts', []))
    
    mount_names = [m['name'] for m in all_mounts]
    for name in mount_names:
        assert any(v['name'] == name for v in volumes), f'Volume mount {name} must reference an existing volume'

def test_service_with_multiple_ports(app_config):
    """Test service generation with multiple ports."""
    config = app_config
    config['ports'] = ['8080:80', '8443:443']
    
    generator = ServiceGenerator(namespace='default')
    services = generator.generate('whoami', config)
    
    # Find the main service
    main_service = next(s for s in services if s['metadata']['name'] == 'whoami')
    
    # Default service should use first port
    ports = main_service['spec']['ports']
    assert len(ports) == 1  # Only first port in default service
    assert ports[0]['name'] == 'default'
    assert ports[0]['port'] == 8080  # First port mapping
    assert ports[0]['targetPort'] == 80  # First container port
    
    # Additional ports should be in LoadBalancer service
    lb_service = next(s for s in services if s['metadata']['name'] == 'whoami-lb')
    lb_ports = lb_service['spec']['ports']
    assert len(lb_ports) == 1  # Second port
    assert lb_ports[0]['port'] == 8443  # Second port mapping
    assert lb_ports[0]['targetPort'] == 443  # Second container port
    
    # Check metrics sidecar service
    metrics_service = next(s for s in services if s['metadata']['name'] == 'whoami-metrics')
    metrics_ports = metrics_service['spec']['ports']
    assert metrics_ports[0]['port'] == 9100

def test_service_types(app_config):
    """Test the three types of services: default ClusterIP, -lb for ports, -ingress for expose."""
    # Test case with all service types
    config = {
        'image': 'traefik/whoami:latest',
        'ports': ['8080:80', '8443:443'],  # Should create -lb service
        'expose': [{'example.com': {'port': 80}}]  # Should create -ingress service
    }
    
    generator = ServiceGenerator(namespace='default')
    services = generator.generate('whoami', config)
    
    # Should have exactly 3 services
    assert len(services) == 3
    
    # 1. Default service (ClusterIP)
    default_service = next(s for s in services if s['metadata']['name'] == 'whoami')
    assert default_service['spec']['type'] == 'ClusterIP'
    assert len(default_service['spec']['ports']) == 1
    assert default_service['spec']['ports'][0]['name'] == 'default'
    assert default_service['spec']['ports'][0]['port'] == 8080
    assert default_service['spec']['ports'][0]['targetPort'] == 80
    
    # 2. LoadBalancer service for additional ports (-lb)
    lb_service = next(s for s in services if s['metadata']['name'] == 'whoami-lb')
    assert lb_service['spec']['type'] == 'LoadBalancer'
    assert len(lb_service['spec']['ports']) == 1
    assert lb_service['spec']['ports'][0]['name'] == 'lb-https'
    assert lb_service['spec']['ports'][0]['port'] == 8443
    assert lb_service['spec']['ports'][0]['targetPort'] == 443
    
    # 3. Ingress service (-ingress)
    ingress_service = next(s for s in services if s['metadata']['name'] == 'whoami-ingress')
    assert ingress_service['spec']['type'] == 'ClusterIP'
    assert len(ingress_service['spec']['ports']) == 1
    assert ingress_service['spec']['ports'][0]['name'] == 'ingress-http'
    assert ingress_service['spec']['ports'][0]['port'] == 80
    assert ingress_service['spec']['ports'][0]['targetPort'] == 80
    
    # Verify no port name clashes
    all_port_names = []
    for service in services:
        all_port_names.extend(p['name'] for p in service['spec']['ports'])
    assert len(all_port_names) == len(set(all_port_names)), "Port names must be unique"

def test_deployment_with_environment_variables(app_config):
    """Test that environment variables are set correctly."""
    config = app_config
    config['environment'] = {
        'DEBUG': 'true',
        'API_KEY': 'secret'
    }
    
    generator = DeploymentGenerator(namespace='default')
    resources = generator.generate('whoami', config)
    
    # Get the deployment
    deployment = resources['deployments'][0]
    
    # Check environment variables in main container
    main_container = deployment['spec']['template']['spec']['containers'][0]
    env_vars = {e['name']: e['value'] for e in main_container['env']}
    
    assert env_vars['DEBUG'] == 'true'
    assert env_vars['API_KEY'] == 'secret'
