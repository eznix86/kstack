# Sidecar Configuration

kstack provides first-class support for sidecar containers, allowing you to enhance your applications with additional functionality like logging, metrics collection, and service mesh proxies.

## Sidecar Basics

Sidecars are defined under the `sidecars` key for each app:

```yaml
apps:
  webapp:
    image: nginx:latest
    sidecars:
      metrics:
        image: prom/node-exporter:latest
```

## Common Sidecar Patterns

### Logging Sidecar
```yaml
apps:
  api:
    image: api:latest
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
        environment:
          FLUENTD_CONF: custom.conf
```

### Metrics Exporter
```yaml
apps:
  webapp:
    image: nginx:latest
    sidecars:
      metrics:
        image: prom/nginx-prometheus-exporter:latest
        ports:
          - "9113:9113"
        environment:
          SCRAPE_URI: "http://localhost/metrics"
```

### Service Mesh Proxy
```yaml
apps:
  service:
    image: myservice:latest
    sidecars:
      proxy:
        image: envoyproxy/envoy:latest
        ports:
          - "15000:15000"
        volumesFrom:
          - config:
              name: envoy-config
              mountPath: /etc/envoy
```

## Sidecar Features

### Volume Sharing
Sidecars can share volumes with the main container:
```yaml
apps:
  app:
    image: app:latest
    volumes:
      - data:/shared
    sidecars:
      backup:
        image: backup:latest
        volumes:
          - data:/shared:ro  # Read-only access
```

### Environment Variables
Sidecars can have their own environment variables:
```yaml
apps:
  app:
    image: app:latest
    environment:
      APP_PORT: 8080
    sidecars:
      metrics:
        image: metrics:latest
        environment:
          SCRAPE_PORT: 8080
```

### Configuration Inheritance
Sidecars can inherit certain configurations from the main app:
- Volumes
- Network settings
- Environment variables

## Best Practices

1. **Keep Sidecars Focused**
   - Each sidecar should have a single responsibility
   - Use separate sidecars for logging, metrics, etc.

2. **Resource Management**
   - Set appropriate resource limits
   - Consider the total resource usage of all containers

3. **Configuration Management**
   - Use ConfigMaps for sidecar configuration
   - Share configurations when appropriate

4. **Security**
   - Use read-only mounts when possible
   - Follow principle of least privilege

## Common Use Cases

1. **Logging and Monitoring**
   - Fluentd for log collection
   - Prometheus exporters for metrics
   - OpenTelemetry collectors

2. **Security and Access Control**
   - Authentication proxies
   - SSL/TLS termination
   - Network policy enforcement

3. **Data Management**
   - Backup agents
   - Cache servers
   - Data transformers

## Troubleshooting

Common issues and solutions:

1. **Volume Mounting Issues**
   - Verify volume names match
   - Check mount paths
   - Ensure proper permissions

2. **Network Connectivity**
   - Confirm ports are correctly mapped
   - Check container DNS resolution
   - Verify service discovery

3. **Resource Constraints**
   - Monitor resource usage
   - Adjust limits if needed
   - Check for OOM kills
