# Best Practices

This guide outlines best practices for using kstack in a Kubernetes-native way.

## Application Structure

### 1. Use Kubernetes-Native Terminology
```yaml
# ✅ Good: Using 'apps' is Kubernetes-native
apps:
  api:
    image: api:latest

# ❌ Bad: Using Docker Compose terminology
services:  # Don't use 'services'
  api:
    image: api:latest
```

### 2. Leverage Sidecars
```yaml
# ✅ Good: Using sidecars for auxiliary containers
apps:
  webapp:
    image: nginx:latest
    sidecars:
      metrics:
        image: prom/node-exporter:latest
      logger:
        image: fluent/fluentd:latest

# ❌ Bad: Using separate top-level apps
apps:
  webapp:
    image: nginx:latest
  webapp-metrics:  # Should be a sidecar
    image: prom/node-exporter:latest
```

### 3. Proper Resource Sharing
```yaml
# ✅ Good: Clear volume sharing between containers
apps:
  api:
    image: api:latest
    volumes:
      - logs:/var/log
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - source: logs
            mountPath: /var/log
```

## Configuration Management

### 1. Environment Variables
```yaml
# ✅ Good: Clear environment structure
apps:
  app:
    image: app:latest
    environment:
      API_URL: https://api.example.com
      DEBUG: "true"
    env_file:
      - ./config/app.env

# ❌ Bad: Mixed environment styles
apps:
  app:
    image: app:latest
    environment:
      - API_URL=https://api.example.com  # Don't use array format
```

### 2. Configuration Files
```yaml
# ✅ Good: Using ConfigMaps for configuration
apps:
  web:
    image: nginx:latest
    volumesFrom:
      - config:
          name: nginx-conf
          mountPath: /etc/nginx/conf.d

# ❌ Bad: Using bind mounts
apps:
  web:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf  # Don't use bind mounts
```

### 3. Secrets Management
```yaml
# ✅ Good: Proper secrets handling
apps:
  db:
    image: postgres:latest
    volumesFrom:
      - config:
          name: db-credentials
          mountPath: /run/secrets
          secret: true

# ❌ Bad: Exposing secrets in environment
apps:
  db:
    image: postgres:latest
    environment:
      DB_PASSWORD: "secret"  # Never expose secrets in plain text
```

## Sidecar Patterns

### 1. Logging Pattern
```yaml
# ✅ Good: Proper logging setup
apps:
  app:
    image: app:latest
    volumes:
      - logs:/var/log
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - source: logs
            mountPath: /var/log
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
```

### 2. Metrics Pattern
```yaml
# ✅ Good: Metrics collection
apps:
  service:
    image: service:latest
    ports:
      - "8080:8080"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

### 3. Proxy Pattern
```yaml
# ✅ Good: Service mesh integration
apps:
  api:
    image: api:latest
    sidecars:
      proxy:
        image: envoyproxy/envoy:latest
        volumesFrom:
          - config:
              name: envoy-config
              mountPath: /etc/envoy
```

## Resource Management

### 1. Resource Limits
```yaml
# ✅ Good: Setting resource constraints
apps:
  app:
    image: app:latest
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
    sidecars:
      cache:
        image: redis:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "200m"
```

### 2. Health Checks
```yaml
# ✅ Good: Proper health monitoring
apps:
  service:
    image: service:latest
    healthcheck:
      path: /health
      port: 8080
      initialDelaySeconds: 10
      periodSeconds: 30
```

## Security Considerations

### 1. Network Policies
```yaml
# ✅ Good: Explicit network policies
apps:
  api:
    image: api:latest
    networkPolicy:
      ingress:
        - from:
            - podSelector:
                matchLabels:
                  role: frontend
```

### 2. Security Context
```yaml
# ✅ Good: Setting security context
apps:
  app:
    image: app:latest
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
```

## Deployment Strategy

### 1. Rolling Updates
```yaml
# ✅ Good: Proper update strategy
apps:
  webapp:
    image: webapp:latest
    deploy:
      replicas: 3
      updateStrategy:
        type: RollingUpdate
        maxUnavailable: 1
```

### 2. Resource Quotas
```yaml
# ✅ Good: Setting resource quotas
apps:
  service:
    image: service:latest
    deploy:
      resources:
        requests:
          memory: "64Mi"
          cpu: "250m"
        limits:
          memory: "128Mi"
          cpu: "500m"
```

## Monitoring and Debugging

### 1. Logging Configuration
```yaml
# ✅ Good: Structured logging
apps:
  app:
    image: app:latest
    environment:
      LOG_FORMAT: json
    sidecars:
      logger:
        image: fluent/fluentd:latest
        environment:
          FLUENT_LOG_LEVEL: info
```

### 2. Metrics Exposure
```yaml
# ✅ Good: Proper metrics exposure
apps:
  service:
    image: service:latest
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - name: metrics
            port: 9100
        annotations:
          prometheus.io/scrape: "true"
          prometheus.io/port: "9100"
```

## General Tips

1. **Keep It Simple**
   - Use clear, descriptive names
   - Maintain consistent structure
   - Document non-obvious choices

2. **Version Control**
   - Version your compose files
   - Document changes
   - Use meaningful commit messages

3. **Testing**
   - Validate configurations before deployment
   - Test with minimal configurations first
   - Use staging environments

4. **Documentation**
   - Document configuration choices
   - Maintain README files
   - Include example configurations
