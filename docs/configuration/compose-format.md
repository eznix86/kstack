# Compose File Format

kstack uses a Kubernetes-native compose file format, designed to bridge the gap between Docker Compose and Kubernetes concepts.

## Basic Structure

```yaml
apps:
  myapp:
    image: nginx:latest
    ports:
      - "8080:80"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
```

## Key Differences from Docker Compose

1. `apps` replaces `services`:
   - More aligned with Kubernetes terminology
   - Better reflects container-centric nature

2. First-class sidecar support:
   - Direct sidecar definition under each app
   - Shared volume and network access
   - Independent configuration

3. Kubernetes-native volume handling:
   - Direct PVC support
   - ConfigMap and Secret mounting
   - Volume sharing between containers

## Example Configurations

### Basic Web Application
```yaml
apps:
  webapp:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - static:/usr/share/nginx/html
```

### Application with Sidecars
```yaml
apps:
  api:
    image: api:latest
    ports:
      - "3000:3000"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
```

### Database with Storage
```yaml
apps:
  db:
    image: postgres:latest
    volumes:
      - data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret
```

## Next Steps
- Learn about [environment configuration](environment.md)
- Explore [volume management](volumes.md)
- Check [sidecar configuration](sidecars.md)
