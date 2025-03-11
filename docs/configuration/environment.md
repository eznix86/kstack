# Environment Variables

kstack provides flexible ways to manage environment variables for both main applications and sidecars.

## Configuration Methods

### 1. Inline Environment Variables
```yaml
apps:
  api:
    image: api:latest
    environment:
      API_KEY: secret
      DEBUG: "true"
      PORT: "3000"
```

### 2. Environment Files
```yaml
apps:
  webapp:
    image: webapp:latest
    env_file:
      - ./config/app.env
      - ./config/common.env
```

### 3. ConfigMap References
```yaml
apps:
  service:
    image: service:latest
    volumesFrom:
      - config:
          name: service-config
          mountPath: /etc/service
```

## Sidecar Environment Variables

Sidecars can have their own environment configuration:

```yaml
apps:
  webapp:
    image: nginx:latest
    environment:
      NGINX_PORT: "80"
    sidecars:
      metrics:
        image: prom/nginx-prometheus-exporter:latest
        environment:
          SCRAPE_URI: "http://localhost/metrics"
          TELEMETRY_PATH: "/metrics"
```

## Configuration Inheritance

Sidecars can inherit environment variables from the main app:

```yaml
apps:
  api:
    image: api:latest
    environment:
      LOG_LEVEL: debug
      APP_NAME: myapi
    env_file:
      - ./common.env
    sidecars:
      logger:
        image: fluent/fluentd:latest
        # Inherits LOG_LEVEL and APP_NAME
        environment:
          FLUENTD_CONF: custom.conf
```

## Best Practices

1. **Security**
   - Never commit sensitive values to version control
   - Use Kubernetes Secrets for sensitive data
   - Consider using external secret management systems

2. **Organization**
   - Group related variables in separate env files
   - Use clear, descriptive variable names
   - Document variable requirements

3. **Configuration Loading**
   - Define a clear loading order
   - Handle defaults appropriately
   - Validate required variables

## Example Configurations

### Development Environment
```yaml
apps:
  app:
    image: myapp:latest
    environment:
      NODE_ENV: development
      DEBUG: "true"
      API_URL: "http://localhost:3000"
```

### Production Environment
```yaml
apps:
  app:
    image: myapp:latest
    environment:
      NODE_ENV: production
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
    sidecars:
      logger:
        image: fluent/fluentd:latest
        environment:
          FLUENT_ELASTICSEARCH_HOST: "elasticsearch"
```

### Multi-Service Setup
```yaml
apps:
  frontend:
    image: frontend:latest
    environment:
      API_URL: "http://backend:8080"
  
  backend:
    image: backend:latest
    environment:
      DB_HOST: "postgres"
      REDIS_URL: "redis://cache:6379"
    sidecars:
      cache:
        image: redis:latest
        environment:
          REDIS_MAXMEMORY: "256mb"
```

## Troubleshooting

Common issues and solutions:

1. **Missing Variables**
   - Check env file paths
   - Verify ConfigMap creation
   - Validate variable names

2. **Inheritance Issues**
   - Confirm inheritance settings
   - Check variable scope
   - Verify sidecar configuration

3. **Secret Management**
   - Ensure secrets are created
   - Check mount paths
   - Verify permissions
