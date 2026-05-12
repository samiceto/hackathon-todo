# Security Hardening Checklist - Step 5

**Step 5: Advanced Cloud Deployment - Security Best Practices**

Use this checklist to secure your Todo App deployment on Minikube or AWS k3s for production use.

---

## Application Security

### Input Validation

- [ ] **Validate all user inputs**
  ```python
  from pydantic import BaseModel, validator, constr

  class TaskCreate(BaseModel):
      title: constr(min_length=1, max_length=200)
      description: constr(max_length=2000) = ""

      @validator('title')
      def title_must_not_be_empty(cls, v):
          if not v.strip():
              raise ValueError('Title cannot be empty')
          return v.strip()
  ```

- [ ] **Sanitize HTML/JavaScript in user content**
  ```python
  import bleach

  def sanitize_input(text: str) -> str:
      return bleach.clean(
          text,
          tags=[],  # No HTML tags allowed
          strip=True
      )
  ```

- [ ] **Prevent SQL injection with parameterized queries**
  ```python
  # Good: Using SQLModel/SQLAlchemy (already safe)
  tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

  # Bad: String concatenation (NEVER do this)
  # query = f"SELECT * FROM tasks WHERE user_id = {user_id}"
  ```

- [ ] **Validate file uploads (if implemented)**
  ```python
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
  MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

  def validate_file(file):
      if file.size > MAX_FILE_SIZE:
          raise ValueError("File too large")

      ext = file.filename.split('.')[-1].lower()
      if ext not in ALLOWED_EXTENSIONS:
          raise ValueError("Invalid file type")
  ```

### Authentication & Authorization

- [ ] **Use strong password requirements**
  ```python
  import re

  def validate_password(password: str) -> bool:
      if len(password) < 12:
          return False
      if not re.search(r'[A-Z]', password):
          return False
      if not re.search(r'[a-z]', password):
          return False
      if not re.search(r'[0-9]', password):
          return False
      if not re.search(r'[!@#$%^&*]', password):
          return False
      return True
  ```

- [ ] **Implement rate limiting**
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter

  @app.post("/auth/login")
  @limiter.limit("5/minute")
  def login(request: Request):
      # Login logic
      pass
  ```

- [ ] **Use secure session management**
  ```python
  # Better Auth configuration
  SESSION_COOKIE_SECURE = True  # HTTPS only
  SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
  SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
  SESSION_MAX_AGE = 3600  # 1 hour
  ```

- [ ] **Implement proper RBAC (Role-Based Access Control)**
  ```python
  from enum import Enum

  class Role(str, Enum):
      ADMIN = "admin"
      USER = "user"
      GUEST = "guest"

  def require_role(required_role: Role):
      def decorator(func):
          @wraps(func)
          def wrapper(*args, **kwargs):
              user = get_current_user()
              if user.role != required_role:
                  raise HTTPException(status_code=403, detail="Insufficient permissions")
              return func(*args, **kwargs)
          return wrapper
      return decorator
  ```

### API Security

- [ ] **Enable CORS with strict origins**
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  # Production: Specific origins only
  ALLOWED_ORIGINS = [
      "https://todo-app.yourdomain.com",
      "https://app.yourdomain.com"
  ]

  app.add_middleware(
      CORSMiddleware,
      allow_origins=ALLOWED_ORIGINS,
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE"],
      allow_headers=["*"],
      max_age=3600
  )
  ```

- [ ] **Add security headers**
  ```python
  from fastapi.middleware.trustedhost import TrustedHostMiddleware

  app.add_middleware(TrustedHostMiddleware, allowed_hosts=["todo-app.yourdomain.com"])

  @app.middleware("http")
  async def add_security_headers(request: Request, call_next):
      response = await call_next(request)
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "DENY"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
      response.headers["Content-Security-Policy"] = "default-src 'self'"
      return response
  ```

- [ ] **Implement request size limits**
  ```python
  from fastapi import Request
  from starlette.middleware.base import BaseHTTPMiddleware

  MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

  class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next):
          if request.headers.get("content-length"):
              content_length = int(request.headers["content-length"])
              if content_length > MAX_REQUEST_SIZE:
                  return Response("Request too large", status_code=413)
          return await call_next(request)

  app.add_middleware(RequestSizeLimitMiddleware)
  ```

- [ ] **Disable debug mode in production**
  ```python
  # In config.py
  DEBUG = os.getenv("DEBUG", "false").lower() == "true"

  # In main.py
  app = FastAPI(debug=DEBUG)
  ```

---

## Secrets Management

### Kubernetes Secrets

- [ ] **Never commit secrets to Git**
  ```bash
  # Add to .gitignore
  echo "*.env" >> .gitignore
  echo "secrets.yaml" >> .gitignore
  echo "*-secret.yaml" >> .gitignore
  ```

- [ ] **Use Kubernetes Secrets for sensitive data**
  ```bash
  # Create secret from literal values
  kubectl create secret generic backend-secret \
    --from-literal=DATABASE_URL="postgresql://..." \
    --from-literal=OPENAI_API_KEY="sk-..." \
    --from-literal=BETTER_AUTH_SECRET="..."

  # Or from file
  kubectl create secret generic backend-secret \
    --from-env-file=.env.production
  ```

- [ ] **Encrypt secrets at rest (cloud providers)**
  ```bash
  # AWS: Enable EBS encryption
  aws ec2 modify-instance-attribute \
    --instance-id <instance-id> \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"Encrypted":true}}]'
  ```

- [ ] **Use external secret management (production)**
  ```bash
  # Install External Secrets Operator
  helm repo add external-secrets https://charts.external-secrets.io
  helm install external-secrets external-secrets/external-secrets

  # Configure AWS Secrets Manager integration
  kubectl apply -f - <<EOF
  apiVersion: external-secrets.io/v1beta1
  kind: SecretStore
  metadata:
    name: aws-secrets
  spec:
    provider:
      aws:
        service: SecretsManager
        region: us-east-1
  EOF
  ```

### Environment Variables

- [ ] **Rotate secrets regularly**
  ```bash
  # Generate new secret
  NEW_SECRET=$(openssl rand -base64 32)

  # Update Kubernetes secret
  kubectl create secret generic backend-secret \
    --from-literal=BETTER_AUTH_SECRET="$NEW_SECRET" \
    --dry-run=client -o yaml | kubectl apply -f -

  # Restart pods to pick up new secret
  kubectl rollout restart deployment todo-app-backend
  ```

- [ ] **Use different secrets per environment**
  ```bash
  # Development
  kubectl create secret generic backend-secret \
    --from-literal=BETTER_AUTH_SECRET="dev-secret-123" \
    --namespace dev

  # Production
  kubectl create secret generic backend-secret \
    --from-literal=BETTER_AUTH_SECRET="prod-secret-xyz" \
    --namespace prod
  ```

---

## Database Security

### Connection Security

- [ ] **Always use SSL/TLS for database connections**
  ```python
  # Neon PostgreSQL (already requires SSL)
  DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require&channel_binding=require"
  ```

- [ ] **Use connection pooling with limits**
  ```python
  engine = create_engine(
      DATABASE_URL,
      pool_size=10,
      max_overflow=5,
      pool_timeout=30,
      pool_recycle=3600
  )
  ```

- [ ] **Restrict database user permissions**
  ```sql
  -- Create application user with limited permissions
  CREATE USER todo_app WITH PASSWORD 'strong_password';
  GRANT CONNECT ON DATABASE todo_db TO todo_app;
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO todo_app;
  GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO todo_app;

  -- Revoke dangerous permissions
  REVOKE CREATE ON SCHEMA public FROM todo_app;
  REVOKE DROP ON ALL TABLES IN SCHEMA public FROM todo_app;
  ```

### Data Protection

- [ ] **Encrypt sensitive data at rest**
  ```python
  from cryptography.fernet import Fernet

  # Generate key (store in secrets)
  key = Fernet.generate_key()
  cipher = Fernet(key)

  def encrypt_field(value: str) -> str:
      return cipher.encrypt(value.encode()).decode()

  def decrypt_field(encrypted: str) -> str:
      return cipher.decrypt(encrypted.encode()).decode()
  ```

- [ ] **Implement data retention policies**
  ```python
  # Delete old completed tasks
  from datetime import datetime, timedelta

  def cleanup_old_tasks():
      cutoff_date = datetime.utcnow() - timedelta(days=90)
      session.exec(
          delete(Task).where(
              Task.completed == True,
              Task.updated_at < cutoff_date
          )
      )
      session.commit()
  ```

- [ ] **Enable database audit logging**
  ```sql
  -- PostgreSQL audit extension
  CREATE EXTENSION IF NOT EXISTS pgaudit;
  ALTER SYSTEM SET pgaudit.log = 'write, ddl';
  SELECT pg_reload_conf();
  ```

---

## Network Security

### Kubernetes Network Policies

- [ ] **Implement network policies to restrict pod communication**
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: backend-network-policy
  spec:
    podSelector:
      matchLabels:
        app.kubernetes.io/component: backend
    policyTypes:
    - Ingress
    - Egress
    ingress:
    - from:
      - podSelector:
          matchLabels:
            app.kubernetes.io/component: frontend
      ports:
      - protocol: TCP
        port: 8000
    egress:
    - to:
      - podSelector:
          matchLabels:
            app: redis
      ports:
      - protocol: TCP
        port: 6379
    - to:
      - podSelector:
          matchLabels:
            app: redpanda
      ports:
      - protocol: TCP
        port: 9092
    - to:  # Allow external database
      - namespaceSelector: {}
      ports:
      - protocol: TCP
        port: 5432
  ```

- [ ] **Restrict ingress to specific sources**
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: frontend-ingress-policy
  spec:
    podSelector:
      matchLabels:
        app.kubernetes.io/component: frontend
    policyTypes:
    - Ingress
    ingress:
    - from:
      - ipBlock:
          cidr: 0.0.0.0/0
          except:
          - 10.0.0.0/8  # Block internal networks
      ports:
      - protocol: TCP
        port: 3000
  ```

### AWS Security Groups

- [ ] **Restrict security group rules to minimum required**
  ```bash
  # Get your IP
  MY_IP=$(curl -s ifconfig.me)

  # Allow SSH only from your IP
  aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr $MY_IP/32

  # Allow HTTP/HTTPS from anywhere
  aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

  aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
  ```

- [ ] **Enable VPC flow logs (AWS)**
  ```bash
  aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-xxxxx \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs
  ```

---

## Container Security

### Image Security

- [ ] **Scan images for vulnerabilities**
  ```bash
  # Install Trivy
  brew install trivy

  # Scan images
  trivy image todo-backend:latest
  trivy image todo-frontend:latest
  trivy image todo-reminder-service:latest

  # Fail build on high/critical vulnerabilities
  trivy image --severity HIGH,CRITICAL --exit-code 1 todo-backend:latest
  ```

- [ ] **Use minimal base images**
  ```dockerfile
  # Good: Alpine-based (small attack surface)
  FROM python:3.13-alpine

  # Better: Distroless (no shell, minimal packages)
  FROM gcr.io/distroless/python3
  ```

- [ ] **Run containers as non-root user**
  ```dockerfile
  # In Dockerfile
  RUN adduser -D -u 1000 appuser
  USER appuser

  # Verify in pod spec
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  ```

- [ ] **Use read-only root filesystem**
  ```yaml
  securityContext:
    readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
    capabilities:
      drop:
      - ALL
  ```

### Pod Security

- [ ] **Enable Pod Security Standards**
  ```yaml
  apiVersion: v1
  kind: Namespace
  metadata:
    name: default
    labels:
      pod-security.kubernetes.io/enforce: restricted
      pod-security.kubernetes.io/audit: restricted
      pod-security.kubernetes.io/warn: restricted
  ```

- [ ] **Disable privilege escalation**
  ```yaml
  securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop:
      - ALL
  ```

- [ ] **Use security context constraints**
  ```yaml
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  ```

---

## Monitoring & Auditing

### Logging

- [ ] **Enable audit logging**
  ```python
  import logging

  audit_logger = logging.getLogger("audit")
  audit_logger.setLevel(logging.INFO)

  def log_audit_event(user_id: int, action: str, resource: str):
      audit_logger.info(
          f"user={user_id} action={action} resource={resource}",
          extra={
              "user_id": user_id,
              "action": action,
              "resource": resource,
              "timestamp": datetime.utcnow().isoformat()
          }
      )
  ```

- [ ] **Log security events**
  ```python
  # Failed login attempts
  @app.post("/auth/login")
  def login(credentials: LoginRequest):
      if not verify_credentials(credentials):
          security_logger.warning(
              f"Failed login attempt for user: {credentials.username}",
              extra={"ip": request.client.host}
          )
          raise HTTPException(status_code=401)
  ```

- [ ] **Centralize logs**
  ```bash
  # Install Loki for log aggregation
  helm repo add grafana https://grafana.github.io/helm-charts
  helm install loki grafana/loki-stack

  # Configure Promtail to collect logs
  kubectl apply -f - <<EOF
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: promtail-config
  data:
    promtail.yaml: |
      server:
        http_listen_port: 9080
      clients:
        - url: http://loki:3100/loki/api/v1/push
      scrape_configs:
        - job_name: kubernetes-pods
          kubernetes_sd_configs:
            - role: pod
  EOF
  ```

### Monitoring

- [ ] **Set up security monitoring alerts**
  ```yaml
  # Prometheus alert rules
  groups:
  - name: security
    rules:
    - alert: HighFailedLoginRate
      expr: rate(failed_login_attempts[5m]) > 10
      annotations:
        summary: "High rate of failed login attempts"

    - alert: UnauthorizedAccessAttempt
      expr: rate(http_requests_total{status="403"}[5m]) > 5
      annotations:
        summary: "Multiple unauthorized access attempts"

    - alert: SuspiciousActivity
      expr: rate(http_requests_total{status="500"}[5m]) > 10
      annotations:
        summary: "High rate of server errors (possible attack)"
  ```

- [ ] **Monitor for CVEs in dependencies**
  ```bash
  # Python dependencies
  pip install safety
  safety check --json

  # Node dependencies
  npm audit --json
  ```

---

## Compliance & Best Practices

### OWASP Top 10

- [ ] **A01: Broken Access Control** - Implement proper RBAC
- [ ] **A02: Cryptographic Failures** - Use TLS, encrypt sensitive data
- [ ] **A03: Injection** - Use parameterized queries, validate inputs
- [ ] **A04: Insecure Design** - Follow security-by-design principles
- [ ] **A05: Security Misconfiguration** - Harden all configurations
- [ ] **A06: Vulnerable Components** - Keep dependencies updated
- [ ] **A07: Authentication Failures** - Implement MFA, strong passwords
- [ ] **A08: Software and Data Integrity** - Verify image signatures
- [ ] **A09: Logging Failures** - Comprehensive audit logging
- [ ] **A10: SSRF** - Validate and sanitize URLs

### Regular Security Tasks

- [ ] **Update dependencies monthly**
  ```bash
  # Python
  pip list --outdated
  pip install --upgrade <package>

  # Node
  npm outdated
  npm update

  # Docker base images
  docker pull python:3.13-alpine
  docker pull node:20-alpine
  ```

- [ ] **Review access logs weekly**
  ```bash
  kubectl logs -l app.kubernetes.io/instance=todo-app --since=7d | grep -E "401|403|500"
  ```

- [ ] **Conduct security audits quarterly**
  - Penetration testing
  - Code review for security issues
  - Dependency vulnerability scan
  - Configuration review

- [ ] **Backup data regularly**
  ```bash
  # Database backup (Neon has automatic backups)
  # Verify backup schedule in Neon dashboard

  # Kubernetes resources backup
  kubectl get all -o yaml > backup-$(date +%Y%m%d).yaml
  ```

---

## Security Checklist Summary

**Application** (8/8):
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] Strong authentication
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] Security headers
- [ ] Request size limits
- [ ] Debug mode disabled

**Secrets** (4/4):
- [ ] No secrets in Git
- [ ] Kubernetes Secrets used
- [ ] Regular secret rotation
- [ ] Environment-specific secrets

**Database** (4/4):
- [ ] SSL/TLS connections
- [ ] Limited user permissions
- [ ] Sensitive data encrypted
- [ ] Audit logging enabled

**Network** (3/3):
- [ ] Network policies configured
- [ ] Security groups restricted
- [ ] VPC flow logs enabled

**Container** (4/4):
- [ ] Images scanned for vulnerabilities
- [ ] Non-root user
- [ ] Read-only filesystem
- [ ] Pod Security Standards enforced

**Monitoring** (3/3):
- [ ] Audit logging enabled
- [ ] Security alerts configured
- [ ] Centralized log aggregation

**Compliance** (3/3):
- [ ] OWASP Top 10 addressed
- [ ] Regular dependency updates
- [ ] Quarterly security audits

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - Security Hardening Checklist
