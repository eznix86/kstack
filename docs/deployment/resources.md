# Resource Generation

kstack generates Kubernetes-native resources from your compose file, ensuring proper integration with the Kubernetes ecosystem.

## Generated Resources

### 1. Deployments
```yaml
apps:
  webapp:
    image: nginx:latest
    ports:
      - "8080:80"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
```

Generates:
- Deployment with main container and sidecar
- Service for port exposure
- ConfigMaps for configuration

### 2. Services
```yaml
apps:
  api:
    image: api:latest
    ports:
      - "3000:3000"
    expose:
      - domain: api.example.com
        port: 3000
```

Generates:
- Service (ClusterIP and LoadBalancer)
- Ingress resource for domain routing

### 3. ConfigMaps
```yaml
apps:
  app:
    image: app:latest
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
```

Generates:
- ConfigMap for configuration files
- Volume mounts in deployment

## Resource Naming

kstack follows consistent naming conventions:

1. **Deployments**: `<app-name>`
2. **Services**: `<app-name>`
3. **ConfigMaps**: `config-<name>`
4. **Volumes**: `vol-<app>-<index>`

## Example Resource Generation

### Input Compose File
```yaml
apps:
  whoami:
    image: traefik/whoami:latest
    ports:
      - "8080:80"
    environment:
      DEBUG: "true"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

### Generated Resources

1. **Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whoami
spec:
  template:
    spec:
      containers:
        - name: whoami
          image: traefik/whoami:latest
          ports:
            - containerPort: 80
          env:
            - name: DEBUG
              value: "true"
        - name: whoami-metrics
          image: prom/node-exporter:latest
          ports:
            - containerPort: 9100
```

2. **Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: whoami
spec:
  ports:
    - port: 8080
      targetPort: 80
  selector:
    app: whoami
```

## Best Practices

1. **Resource Organization**
   - Use meaningful app names
   - Group related services
   - Maintain consistent naming

2. **Sidecar Integration**
   - Define clear container responsibilities
   - Share resources appropriately
   - Set proper resource limits

3. **Configuration Management**
   - Use ConfigMaps for configuration
   - Separate sensitive data into Secrets
   - Version control configurations

## Validation

kstack validates resources before creation:

1. **Schema Validation**
   - Correct resource structure
   - Required fields present
   - Valid field values

2. **Relationship Validation**
   - Volume references exist
   - Service ports match
   - ConfigMap names valid

3. **Kubernetes Compatibility**
   - API versions supported
   - Resource limits within bounds
   - Feature gates enabled

## Troubleshooting

Common issues and solutions:

1. **Resource Creation Failures**
   - Check resource quotas
   - Verify permissions
   - Validate resource specs

2. **Naming Conflicts**
   - Use unique app names
   - Check existing resources
   - Follow naming conventions

3. **Configuration Issues**
   - Verify ConfigMap content
   - Check volume mounts
   - Validate environment variables
