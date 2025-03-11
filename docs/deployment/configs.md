# ConfigMaps and Secrets

kstack provides comprehensive support for managing application configuration through ConfigMaps and Secrets, with automatic conversion from environment variables and configuration files.

## Configuration Methods

### 1. Inline Environment Variables
Automatically converted to ConfigMaps:
```yaml
apps:
  api:
    image: api:latest
    environment:
      API_URL: https://api.example.com
      DEBUG: "true"
      LOG_LEVEL: info
```

### 2. Environment Files
Support for multiple .env files:
```yaml
apps:
  webapp:
    image: webapp:latest
    env_file:
      - ./config/app.env
      - ./config/common.env
    sidecars:
      logger:
        image: fluent/fluentd:latest
        env_file:
          - ./config/logging.env
```

### 3. External ConfigMaps
Reference existing Kubernetes resources:
```yaml
apps:
  service:
    image: service:latest
    volumesFrom:
      - config:
          name: service-config
          mountPath: /etc/service
```

## Sidecar Configuration

Each sidecar can have its own configuration:

```yaml
apps:
  web:
    image: nginx:latest
    volumesFrom:
      - config:
          name: nginx-conf
          mountPath: /etc/nginx/conf.d
    sidecars:
      logger:
        image: fluent/fluentd:latest
        environment:
          FLUENTD_CONF: custom.conf
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
```

## Configuration Loading Order

kstack preserves the correct loading order:

1. Default values
2. Environment files (in order specified)
3. Inline environment variables
4. External ConfigMaps and Secrets

## Common Patterns

### 1. Application Configuration
```yaml
apps:
  app:
    image: app:latest
    environment:
      APP_ENV: production
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
```

### 2. Logging Configuration
```yaml
apps:
  service:
    image: service:latest
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
              subPath: fluent.conf
```

### 3. Metrics Configuration
```yaml
apps:
  api:
    image: api:latest
    sidecars:
      metrics:
        image: prom/prometheus:latest
        volumesFrom:
          - config:
              name: prometheus-config
              mountPath: /etc/prometheus
```

## Best Practices

1. **Security**
   - Use Secrets for sensitive data
   - Avoid hardcoding credentials
   - Implement proper RBAC

2. **Organization**
   - Group related configurations
   - Use meaningful names
   - Document configuration structure

3. **Maintenance**
   - Version control configurations
   - Implement change tracking
   - Plan for updates

## Example Configurations

### 1. Web Application
```yaml
apps:
  webapp:
    image: nginx:latest
    volumesFrom:
      - config:
          name: nginx-conf
          mountPath: /etc/nginx/conf.d
      - config:
          name: ssl-certs
          mountPath: /etc/nginx/ssl
          secret: true
```

### 2. Database with Secrets
```yaml
apps:
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_USER: "admin"
    volumesFrom:
      - config:
          name: db-password
          mountPath: /run/secrets
          secret: true
```

### 3. Microservice with Multiple Configs
```yaml
apps:
  service:
    image: service:latest
    env_file:
      - ./config/service.env
    volumesFrom:
      - config:
          name: service-config
          mountPath: /etc/service
    sidecars:
      cache:
        image: redis:latest
        volumesFrom:
          - config:
              name: redis-config
              mountPath: /usr/local/etc/redis
```

## Troubleshooting

Common issues and solutions:

1. **ConfigMap Loading**
   - Verify ConfigMap exists
   - Check mount paths
   - Validate file permissions

2. **Secret Management**
   - Ensure secrets are created
   - Check secret references
   - Verify access rights

3. **Environment Variables**
   - Check variable names
   - Verify file paths
   - Validate value formats

4. **Sidecar Configuration**
   - Confirm config inheritance
   - Check mount points
   - Verify config updates
