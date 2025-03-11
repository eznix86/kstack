# kstack

A Kubernetes-native tool that simplifies application deployment by converting Docker Compose files to Kubernetes resources. Built for modern cloud-native applications with first-class support for sidecars and configuration management.

## Features

✨ **Kubernetes-Native**
- Deployments, Services, and ConfigMaps
- First-class sidecar support
- Volume sharing between containers

🔧 **Easy Configuration**
- Environment variables
- Config files
- Secrets management

🚀 **Simple to Use**
- Intuitive CLI commands
- Automatic resource generation
- Built-in validation

## Quick Start

1. Install kstack:
```bash
poetry install
```

2. Create a compose file (`whoami-compose.yaml`):
```yaml
apps:
  whoami:
    image: traefik/whoami:latest
    ports:
      - "8080:80"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

3. Deploy to Kubernetes:
```bash
kstack apply whoami-compose.yaml
```

## Basic Commands

```bash
# Convert to Kubernetes YAML
kstack convert app-compose.yaml

# Deploy to cluster
kstack apply app-compose.yaml

# Remove from cluster
kstack destroy app-compose.yaml
```

## Configuration Examples

### Environment Variables
```yaml
apps:
  api:
    image: api:latest
    environment:
      API_KEY: secret
      DEBUG: "true"
```

### Volumes
```yaml
apps:
  db:
    image: postgres:latest
    volumes:
      - data:/var/lib/postgresql/data
```

### Sidecars
```yaml
apps:
  web:
    image: nginx:latest
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
```

## Need Help?

- Check out our [example directory](./example) for more samples
- File an issue on GitHub for bugs or feature requests
- Read our [documentation](./docs) for detailed information
