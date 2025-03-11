# Volume Management

kstack provides Kubernetes-native volume management, supporting both application data storage and configuration sharing between containers.

## Volume Types

### 1. Persistent Volumes
```yaml
apps:
  db:
    image: postgres:latest
    volumes:
      - data:/var/lib/postgresql/data  # Named volume
      - /host/path:/container/path     # Host path
```

### 2. Configuration Volumes
```yaml
apps:
  app:
    image: app:latest
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
```

### 3. Shared Volumes
Volumes shared between main app and sidecars:
```yaml
apps:
  web:
    image: nginx:latest
    volumes:
      - logs:/var/log/nginx
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - source: logs
            mountPath: /fluentd/log
```

## Volume Inheritance

Sidecars automatically inherit volumes from the main app:

```yaml
apps:
  api:
    image: api:latest
    volumes:
      - data:/shared/data
    sidecars:
      backup:
        image: backup:latest
        # Inherits data volume automatically
        environment:
          BACKUP_DIR: /shared/data
```

## Common Patterns

### 1. Database Storage
```yaml
apps:
  postgres:
    image: postgres:latest
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret
```

### 2. Configuration Files
```yaml
apps:
  nginx:
    image: nginx:latest
    volumesFrom:
      - config:
          name: nginx-conf
          mountPath: /etc/nginx/conf.d
```

### 3. Shared Logging
```yaml
apps:
  app:
    image: app:latest
    volumes:
      - logs:/var/log
    sidecars:
      filebeat:
        image: elastic/filebeat:latest
        volumesFrom:
          - source: logs
            mountPath: /var/log
          - config:
              name: filebeat-config
              mountPath: /usr/share/filebeat/filebeat.yml
              subPath: filebeat.yml
```

## Best Practices

1. **Data Persistence**
   - Use named volumes for persistent data
   - Consider backup strategies
   - Set appropriate access modes

2. **Configuration Management**
   - Use ConfigMaps for configuration files
   - Version control your configurations
   - Keep configurations separate from code

3. **Security**
   - Use read-only mounts when possible
   - Set appropriate file permissions
   - Follow principle of least privilege

4. **Resource Management**
   - Set storage requests and limits
   - Monitor volume usage
   - Plan for scaling

## Volume Sharing Strategies

### 1. Read-Write Sharing
```yaml
apps:
  app:
    image: app:latest
    volumes:
      - data:/shared/data
    sidecars:
      processor:
        image: processor:latest
        # Full read-write access
        volumesFrom:
          - source: data
            mountPath: /shared/data
```

### 2. Read-Only Access
```yaml
apps:
  web:
    image: nginx:latest
    volumesFrom:
      - config:
          name: static-content
          mountPath: /usr/share/nginx/html
          readOnly: true
```

### 3. Selective Mounting
```yaml
apps:
  app:
    image: app:latest
    volumes:
      - config:/etc/app
      - data:/var/lib/app
      - logs:/var/log/app
    sidecars:
      logger:
        # Only mount necessary volumes
        volumesFrom:
          - source: logs
            mountPath: /var/log/app
```

## Troubleshooting

Common issues and solutions:

1. **Permission Issues**
   - Check file ownership
   - Verify SELinux contexts
   - Review mount options

2. **Storage Issues**
   - Monitor storage capacity
   - Check PVC binding status
   - Verify storage class availability

3. **Configuration Issues**
   - Validate ConfigMap content
   - Check mount paths
   - Verify volume names
