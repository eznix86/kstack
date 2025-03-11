# Troubleshooting Guide

Common issues and solutions when using kstack.

## Configuration Issues

### 1. Environment Variables Not Applied

**Problem**: Environment variables not appearing in containers

**Check**:
```yaml
# Check your configuration
apps:
  api:
    image: api:latest
    environment:
      DEBUG: "true"  # Make sure values are strings
```

**Solutions**:
1. Verify environment variable format
2. Check ConfigMap generation
3. Validate volume mounts

### 2. Sidecar Configuration Not Inherited

**Problem**: Sidecar missing inherited configuration

**Check**:
```yaml
apps:
  web:
    image: nginx:latest
    volumes:
      - logs:/var/log
    sidecars:
      logger:
        image: fluent/fluentd:latest
        # Should automatically inherit volumes
```

**Solutions**:
1. Verify main app configuration
2. Check sidecar specification
3. Validate volume references

## Volume Management

### 1. Volume Mount Failures

**Problem**: Containers can't access volumes

**Check**:
```yaml
apps:
  app:
    image: app:latest
    volumesFrom:
      - config:
          name: app-config
          mountPath: /etc/app
```

**Solutions**:
1. Verify ConfigMap exists
2. Check mount paths
3. Validate permissions

### 2. Shared Volume Issues

**Problem**: Sidecars can't access shared volumes

**Check**:
```yaml
apps:
  service:
    image: service:latest
    volumes:
      - data:/shared
    sidecars:
      backup:
        image: backup:latest
        volumesFrom:
          - source: data
            mountPath: /shared
```

**Solutions**:
1. Check volume definitions
2. Verify mount paths
3. Validate permissions

## Service Discovery

### 1. Service Communication Failures

**Problem**: Services can't communicate

**Check**:
```yaml
apps:
  frontend:
    image: frontend:latest
    environment:
      API_URL: "http://backend:3000"
  
  backend:
    image: backend:latest
    ports:
      - "3000:3000"
```

**Solutions**:
1. Check service names
2. Verify port mappings
3. Validate network policies

### 2. External Access Issues

**Problem**: Cannot access services externally

**Check**:
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

**Solutions**:
1. Check ingress configuration
2. Verify port mappings
3. Validate domain settings

## Sidecar Issues

### 1. Sidecar Not Starting

**Problem**: Sidecar containers fail to start

**Check**:
```yaml
apps:
  app:
    image: app:latest
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

**Solutions**:
1. Check image availability
2. Verify resource limits
3. Validate configuration

### 2. Sidecar Communication Issues

**Problem**: Main app can't communicate with sidecars

**Check**:
```yaml
apps:
  web:
    image: nginx:latest
    environment:
      METRICS_URL: "http://localhost:9100"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
```

**Solutions**:
1. Check localhost references
2. Verify port mappings
3. Validate network policies

## Resource Management

### 1. Resource Limit Issues

**Problem**: Containers being OOM killed

**Check**:
```yaml
apps:
  app:
    image: app:latest
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
```

**Solutions**:
1. Adjust resource limits
2. Monitor resource usage
3. Check application requirements

### 2. Scaling Issues

**Problem**: Applications not scaling properly

**Check**:
```yaml
apps:
  service:
    image: service:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: "128Mi"
```

**Solutions**:
1. Check resource availability
2. Verify scaling configuration
3. Validate cluster capacity

## Common Commands

### Validation
```bash
# Validate compose file
kstack validate app-compose.yaml

# Check generated resources
kstack convert app-compose.yaml --output-dir k8s
```

### Debugging
```bash
# Get deployment status
kubectl get pods

# Check container logs
kubectl logs <pod-name> -c <container-name>

# Describe resources
kubectl describe pod <pod-name>
```

## Debug Checklist

1. **Configuration**
   - [ ] Validate compose file syntax
   - [ ] Check environment variables
   - [ ] Verify volume mounts

2. **Resources**
   - [ ] Check pod status
   - [ ] Review container logs
   - [ ] Monitor resource usage

3. **Networking**
   - [ ] Verify service discovery
   - [ ] Check port mappings
   - [ ] Validate ingress rules

4. **Sidecars**
   - [ ] Check sidecar status
   - [ ] Verify configuration inheritance
   - [ ] Review shared resources

## Getting Help

1. **Documentation**
   - Check the relevant documentation sections
   - Review example configurations
   - Look for similar issues

2. **Logs**
   - Collect relevant logs
   - Enable debug logging
   - Check events

3. **Support**
   - File detailed bug reports
   - Include minimal reproduction
   - Share relevant configurations

## Prevention Tips

1. **Testing**
   - Test configurations in staging
   - Use minimal examples first
   - Validate before deployment

2. **Monitoring**
   - Set up proper logging
   - Monitor resource usage
   - Track application metrics

3. **Documentation**
   - Document configurations
   - Note special requirements
   - Share solutions
