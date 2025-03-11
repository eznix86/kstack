# Migration Guide

This guide helps you migrate your Docker Compose applications to kstack's Kubernetes-native format.

## Key Changes

### 1. Terminology Updates

#### From Docker Compose:
```yaml
version: '3'
services:
  webapp:
    image: nginx:latest
```

#### To kstack:
```yaml
apps:
  webapp:
    image: nginx:latest
```

### 2. Sidecar Support

#### From Multiple Services:
```yaml
version: '3'
services:
  webapp:
    image: nginx:latest
  metrics:
    image: prom/node-exporter:latest
```

#### To Sidecars:
```yaml
apps:
  webapp:
    image: nginx:latest
    sidecars:
      metrics:
        image: prom/node-exporter:latest
```

### 3. Configuration Management

#### From Docker Compose:
```yaml
services:
  app:
    environment:
      - DEBUG=true
    volumes:
      - ./config:/etc/app
```

#### To kstack:
```yaml
apps:
  app:
    environment:
      DEBUG: "true"
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
```

## Migration Steps

1. **Update File Structure**
   - Remove version field
   - Rename 'services' to 'apps'
   - Move auxiliary containers to sidecars

2. **Update Volume Configuration**
   - Convert bind mounts to ConfigMaps
   - Update volume syntax
   - Configure volume sharing

3. **Update Environment Variables**
   - Convert environment arrays to maps
   - Move configs to ConfigMaps
   - Update secret references

## Common Use Cases

### 1. Web Application

#### From Docker Compose:
```yaml
version: '3'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  metrics:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

#### To kstack:
```yaml
apps:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

### 2. Logging Setup

#### From Docker Compose:
```yaml
version: '3'
services:
  app:
    image: app:latest
    volumes:
      - ./logs:/var/log
  logger:
    image: fluent/fluentd:latest
    volumes:
      - ./logs:/var/log
      - ./fluentd:/etc/fluentd
```

#### To kstack:
```yaml
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
              mountPath: /etc/fluentd
```

### 3. Database Configuration

#### From Docker Compose:
```yaml
version: '3'
services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./secrets:/run/secrets
```

#### To kstack:
```yaml
apps:
  db:
    image: postgres:latest
    volumes:
      - data:/var/lib/postgresql/data
    volumesFrom:
      - config:
          name: db-password
          mountPath: /run/secrets
          secret: true
```

## Best Practices

1. **Service Organization**
   - Group related containers as sidecars
   - Use meaningful app names
   - Maintain clear dependencies

2. **Configuration Management**
   - Use ConfigMaps for configuration
   - Convert secrets appropriately
   - Maintain configuration hierarchy

3. **Resource Sharing**
   - Configure volume sharing properly
   - Set up network policies
   - Manage resource limits

## Troubleshooting

Common migration issues and solutions:

1. **Volume Mounting**
   - Issue: Bind mounts don't work
   - Solution: Convert to ConfigMaps or PVCs

2. **Network Configuration**
   - Issue: Services can't communicate
   - Solution: Use Kubernetes DNS names

3. **Environment Variables**
   - Issue: Complex env files
   - Solution: Split into multiple ConfigMaps

## Validation

After migration:

1. **Check Resources**
```bash
kstack validate app-compose.yaml
```

2. **Review Generated Config**
```bash
kstack convert app-compose.yaml --output-dir k8s
```

3. **Test Deployment**
```bash
kstack apply app-compose.yaml
```
