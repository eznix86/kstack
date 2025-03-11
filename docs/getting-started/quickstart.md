# Quick Start Guide

This guide will help you deploy your first application using kstack's Kubernetes-native approach.

## Simple Application Deployment

1. Create a compose file (`whoami-compose.yaml`):
```yaml
apps:  # Using 'apps' instead of 'services' for Kubernetes-native terminology
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

2. Deploy to Kubernetes:
```bash
kstack apply whoami-compose.yaml
```

3. Verify deployment:
```bash
kubectl get pods
kubectl get services
```

## Adding a Logging Sidecar

Enhance your application with a Fluentd logging sidecar:

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
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
        environment:
          FLUENTD_CONF: custom.conf
```

## Next Steps

- Learn about [environment configuration](../configuration/environment.md)
- Explore [sidecar patterns](../configuration/sidecars.md)
- Check [service configuration](../deployment/services.md)
