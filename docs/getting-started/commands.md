# Basic Commands

kstack provides an intuitive CLI for managing your Kubernetes-native applications.

## Core Commands

### Convert
Convert a compose file to Kubernetes manifests:
```bash
kstack convert whoami-compose.yaml
```

Options:
- `--output-dir`, `-o`: Output directory (default: ./k8s)
- `--namespace`, `-n`: Kubernetes namespace (default: default)

### Apply
Deploy an application to Kubernetes:
```bash
kstack apply whoami-compose.yaml
```

Options:
- `--namespace`, `-n`: Target namespace
- `--skip-k8s-check`: Skip Kubernetes connection check

### Destroy
Remove an application from Kubernetes:
```bash
kstack destroy whoami-compose.yaml
```

Options:
- `--force`: Skip confirmation
- `--namespace`, `-n`: Target namespace

### Validate
Check a compose file for correctness:
```bash
kstack validate whoami-compose.yaml
```

## Example Usage

### 1. Basic Web Application
```bash
# Create a compose file
cat > whoami-compose.yaml <<EOF
apps:
  whoami:
    image: traefik/whoami:latest
    ports:
      - "8080:80"
    sidecars:
      metrics:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
EOF

# Validate the configuration
kstack validate whoami-compose.yaml

# Deploy to Kubernetes
kstack apply whoami-compose.yaml
```

### 2. Application with Configuration
```bash
# Create a compose file with configuration
cat > app-compose.yaml <<EOF
apps:
  api:
    image: api:latest
    environment:
      DEBUG: "true"
    volumesFrom:
      - config:
          name: api-config
          mountPath: /etc/api
    sidecars:
      logger:
        image: fluent/fluentd:latest
        volumesFrom:
          - config:
              name: fluentd-config
              mountPath: /fluentd/etc
EOF

# Generate Kubernetes manifests
kstack convert app-compose.yaml -o k8s-manifests

# Review and apply
kstack apply app-compose.yaml
```

### 3. Multi-Container Application
```bash
# Deploy a web application with sidecars
cat > web-compose.yaml <<EOF
apps:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    sidecars:
      metrics:
        image: prom/nginx-prometheus-exporter:latest
        ports:
          - "9113:9113"
      logger:
        image: fluent/fluentd:latest
        environment:
          FLUENTD_CONF: custom.conf
EOF

# Deploy to a specific namespace
kstack apply web-compose.yaml -n web-apps
```

## Command Flow

1. **Development Flow**:
   ```bash
   # 1. Create compose file
   vim app-compose.yaml

   # 2. Validate configuration
   kstack validate app-compose.yaml

   # 3. Generate manifests for review
   kstack convert app-compose.yaml -o k8s

   # 4. Deploy to Kubernetes
   kstack apply app-compose.yaml
   ```

2. **Update Flow**:
   ```bash
   # 1. Modify compose file
   vim app-compose.yaml

   # 2. Validate changes
   kstack validate app-compose.yaml

   # 3. Apply updates
   kstack apply app-compose.yaml
   ```

3. **Cleanup Flow**:
   ```bash
   # Remove application
   kstack destroy app-compose.yaml --force
   ```

## Best Practices

1. **Validation**
   - Always validate configurations before deployment
   - Review generated manifests
   - Test in a staging environment

2. **Namespace Management**
   - Use meaningful namespace names
   - Isolate different environments
   - Consider resource quotas

3. **Resource Management**
   - Monitor resource usage
   - Set appropriate limits
   - Plan for scaling

## Common Issues

1. **Connection Problems**
   ```bash
   # Check Kubernetes connection
   kubectl cluster-info

   # Then try kstack
   kstack apply app-compose.yaml --skip-k8s-check
   ```

2. **Resource Conflicts**
   ```bash
   # Check existing resources
   kubectl get all -n <namespace>

   # Force cleanup if needed
   kstack destroy app-compose.yaml --force
   ```

3. **Configuration Issues**
   ```bash
   # Validate configuration
   kstack validate app-compose.yaml

   # Check generated manifests
   kstack convert app-compose.yaml -o debug
   ```

## Tips and Tricks

1. **Quick Validation**
   ```bash
   # Validate and show issues
   kstack validate app-compose.yaml
   ```

2. **Manifest Generation**
   ```bash
   # Generate and review
   kstack convert app-compose.yaml -o review
   ```

3. **Namespace Isolation**
   ```bash
   # Deploy to isolated namespace
   kstack apply app-compose.yaml -n my-app
   ```

Remember to check the logs and status of your deployments after applying changes:
```bash
# Check pod status
kubectl get pods -n <namespace>

# View container logs
kubectl logs <pod-name> -c <container-name> -n <namespace>
```
