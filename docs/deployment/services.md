# Service Configuration

kstack provides Kubernetes-native service configuration, allowing you to expose your applications both internally and externally.

## Service Types

### 1. Internal Services (ClusterIP)
```yaml
apps:
  api:
    image: api:latest
    ports:
      - "3000:3000"  # Internal access only
```

### 2. External Services (LoadBalancer)
```yaml
apps:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    expose:
      - domain: www.example.com
        port: 80
```

### 3. Ingress Configuration
```yaml
apps:
  app:
    image: app:latest
    ports:
      - "8080:80"
    expose:
      - domain: app.example.com
        ingressClassName: traefik
        port: 8080
        protocol: http
```

## Port Configuration

### 1. Basic Port Mapping
```yaml
apps:
  web:
    image: nginx:latest
    ports:
      - "8080:80"      # Host:Container
      - "8443:443"     # Multiple ports
```

### 2. Protocol Specification
```yaml
apps:
  api:
    image: api:latest
    ports:
      - "9000:9000/tcp"  # Explicit TCP
      - "514:514/udp"    # UDP port
```

### 3. Named Ports
```yaml
apps:
  app:
    image: app:latest
    ports:
      - name: http
        port: 8080
        targetPort: 80
      - name: metrics
        port: 9100
```

## Service Discovery

### 1. Internal DNS
Services are automatically registered with Kubernetes DNS:
```yaml
apps:
  frontend:
    image: frontend:latest
    environment:
      API_URL: "http://backend:3000"  # DNS-based service discovery
  
  backend:
    image: backend:latest
    ports:
      - "3000:3000"
```

### 2. Cross-Namespace Access
```yaml
apps:
  app:
    image: app:latest
    environment:
      DB_HOST: "postgres.db.svc.cluster.local"  # Full DNS name
```

## Advanced Configurations

### 1. Health Checks
```yaml
apps:
  api:
    image: api:latest
    healthcheck:
      path: /health
      port: 8080
      initialDelaySeconds: 10
      periodSeconds: 30
```

### 2. Traffic Policies
```yaml
apps:
  db:
    image: postgres:latest
    service:
      type: ClusterIP
      externalTrafficPolicy: Local
```

### 3. Session Affinity
```yaml
apps:
  webapp:
    image: webapp:latest
    service:
      sessionAffinity: ClientIP
      sessionAffinityConfig:
        clientIP:
          timeoutSeconds: 10800
```

## Best Practices

1. **Port Management**
   - Use standard ports when possible
   - Document port assignments
   - Avoid port conflicts

2. **Service Exposure**
   - Limit external exposure
   - Use appropriate service types
   - Implement proper security

3. **Load Balancing**
   - Configure health checks
   - Set appropriate timeouts
   - Consider session affinity

## Example Configurations

### 1. Web Application Stack
```yaml
apps:
  frontend:
    image: frontend:latest
    ports:
      - "80:80"
    expose:
      - domain: www.example.com
        ingressClassName: nginx
        port: 80
  
  api:
    image: api:latest
    ports:
      - "3000:3000"  # Internal only
    environment:
      DB_HOST: db
  
  db:
    image: postgres:latest
    ports:
      - "5432:5432"  # Internal only
```

### 2. Microservices Setup
```yaml
apps:
  auth:
    image: auth-service:latest
    ports:
      - name: http
        port: 8080
      - name: metrics
        port: 9100
    sidecars:
      metrics:
        image: prom/node-exporter:latest
  
  users:
    image: user-service:latest
    ports:
      - "8081:8080"
    environment:
      AUTH_URL: "http://auth:8080"
```

## Troubleshooting

Common issues and solutions:

1. **Service Discovery Issues**
   - Check DNS resolution
   - Verify service names
   - Check namespace configuration

2. **Port Conflicts**
   - Review port assignments
   - Check for duplicates
   - Verify port availability

3. **Load Balancer Problems**
   - Check service type
   - Verify health checks
   - Review traffic policies
