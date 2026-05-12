# Technology Decisions: Step 5 - Advanced Cloud Deployment

**Created**: 2026-01-30
**Purpose**: Document key technology choices, trade-offs, and rationale for Step 5 implementation

## Overview

This document captures the 7 critical technology decisions made during the planning phase (Phase 0) for Step 5: Advanced Cloud Deployment.

---

## Decision 1: RRULE Parsing Library

### Decision

**Selected**: `python-dateutil` (https://github.com/dateutil/dateutil)

### Alternatives Considered

1. **python-dateutil** ✅
   - Pros: RFC 5545 compliant, battle-tested, widely used, handles edge cases
   - Cons: Heavier dependency, includes features we don't need
   - Performance: Excellent for our use case (<1ms per RRULE parse)

2. **dateutil.rrule (built-in)**
   - Pros: Already part of python-dateutil
   - Cons: Same as option 1
   - Note: This is the same as option 1 (python-dateutil includes rrule module)

3. **Custom RRULE parser**
   - Pros: Lightweight, only what we need
   - Cons: High complexity, error-prone, reinventing the wheel
   - Risk: Missing edge cases, timezone issues, daylight saving time bugs

### Rationale

python-dateutil is the industry standard for RFC 5545 RRULE parsing in Python. It handles complex edge cases like:
- Timezone conversions
- Daylight saving time transitions
- Leap years and month boundaries
- Complex RRULE patterns (BYDAY, BYMONTHDAY, BYHOUR, etc.)
- UNTIL and COUNT limits

### Implementation Notes

```python
from dateutil.rrule import rrulestr
from datetime import datetime

# Parse RRULE string
rule = rrulestr("FREQ=DAILY;COUNT=5", dtstart=datetime.now())

# Get next occurrence
next_occurrence = rule.after(datetime.now())
```

### Risk Mitigation

- Validate RRULE format before parsing (catch exceptions)
- Set reasonable limits on recurrence complexity (e.g., max 100 occurrences)
- Document supported RRULE features in API documentation

---

## Decision 2: Kafka Broker Selection

### Decision

**Development (Minikube)**: Redpanda (https://redpanda.com/)
**Production (Cloud)**: Confluent Cloud or Redpanda Cloud

### Alternatives Considered

1. **Redpanda (Minikube)** ✅
   - Pros: Kafka-compatible, lightweight, easy to deploy, no Zookeeper
   - Cons: Less mature than Kafka, smaller community
   - Resource Usage: 256MB RAM, 1 CPU core (vs Kafka: 1GB+ RAM, 2+ cores)

2. **Apache Kafka (Minikube)**
   - Pros: Industry standard, mature, extensive documentation
   - Cons: Heavy resource requirements, requires Zookeeper, complex setup
   - Resource Usage: 1GB+ RAM, 2+ CPU cores (too heavy for Minikube)

3. **Confluent Cloud (Production)** ✅
   - Pros: Fully managed, auto-scaling, enterprise features, 99.95% SLA
   - Cons: Cost ($1/hour cluster + $0.11/GB ingress), vendor lock-in
   - Cost Estimate: $100-200/month for dev/staging, $500+/month for production

4. **Redpanda Cloud (Production)** ✅
   - Pros: Kafka-compatible, lower cost, simpler pricing, good performance
   - Cons: Newer service, fewer integrations
   - Cost Estimate: $50-100/month for dev/staging, $300+/month for production

5. **Self-Hosted Kafka (Cloud Kubernetes)**
   - Pros: Full control, no vendor lock-in, predictable costs
   - Cons: Operational complexity, requires expertise, 24/7 monitoring
   - Effort: 2-3 engineers for setup + ongoing maintenance

### Rationale

**Minikube (Development)**:
Redpanda is the clear winner for local development:
- Runs in <300MB RAM (Minikube typically has 2-4GB total)
- Single-node deployment (no clustering complexity)
- Kafka-compatible API (same Dapr Pub/Sub component works for both)
- Fast startup (<10 seconds vs Kafka's 30-60 seconds)

**Production (Cloud)**:
Managed Kafka services eliminate operational complexity:
- No need to manage brokers, replicas, or upgrades
- Auto-scaling handles traffic spikes
- Built-in monitoring and alerting
- High availability with multi-AZ replication

Choice between Confluent Cloud and Redpanda Cloud depends on:
- Budget: Redpanda Cloud is 30-40% cheaper
- Features: Confluent Cloud has more enterprise features (Schema Registry, ksqlDB, Connectors)
- Support: Both offer enterprise support

### Implementation Notes

**Dapr Abstraction**:
Using Dapr Pub/Sub component provides portability:
- Same application code works with Redpanda, Confluent, AWS MSK, Azure Event Hubs
- Only change Dapr component YAML to switch providers
- Fallback option: If Kafka access is blocked, switch to Redis Streams or Azure Service Bus

**Helm Configuration**:
```yaml
# values-dev.yaml (Minikube)
kafka:
  provider: redpanda
  brokers: "redpanda-0.redpanda.default.svc.cluster.local:9092"

# values-prod.yaml (Confluent Cloud)
kafka:
  provider: confluent-cloud
  brokers: "pkc-xxxxx.us-west-2.aws.confluent.cloud:9092"
  sasl:
    mechanism: SCRAM-SHA-256
    username: <from-secret>
    password: <from-secret>
```

### Risk Mitigation

- Dapr abstraction allows switching Kafka providers without code changes
- Document fallback to alternative Pub/Sub (Redis Streams, Azure Service Bus)
- Set up monitoring for Kafka lag, throughput, error rates
- Test Kafka failover scenarios (broker failure, network partition)

---

## Decision 3: Cloud Platform Guidance

### Decision

**Support All Three**: Azure AKS, Google Cloud GKE, Oracle Cloud OKE

### Rationale

Rather than choosing a single cloud platform, we support all three via Helm values files:

- `values-prod-aks.yaml`: Azure-specific configuration
- `values-prod-gke.yaml`: Google Cloud-specific configuration
- `values-prod-oke.yaml`: Oracle Cloud-specific configuration

This approach:
1. Demonstrates multi-cloud portability
2. Allows users to choose based on their existing cloud provider
3. Uses Dapr and Kubernetes for cloud-agnostic abstractions

### Implementation Notes

**Managed Services Mapping**:

| Service | Azure (AKS) | Google Cloud (GKE) | Oracle Cloud (OKE) |
|---------|-------------|--------------------|--------------------|
| Kubernetes | Azure Kubernetes Service | Google Kubernetes Engine | Oracle Container Engine |
| PostgreSQL | Azure Database for PostgreSQL | Cloud SQL for PostgreSQL | Oracle Autonomous Database |
| Redis | Azure Cache for Redis | Cloud Memorystore | Oracle OCI Cache |
| Kafka | Confluent Cloud or Redpanda Cloud | Confluent Cloud or Redpanda Cloud | Confluent Cloud or Redpanda Cloud |
| Load Balancer | Azure Load Balancer | Cloud Load Balancing | Oracle Load Balancer |
| DNS | Azure DNS | Cloud DNS | Oracle DNS |
| Secrets | Azure Key Vault or K8s Secrets | Secret Manager or K8s Secrets | Oracle Vault or K8s Secrets |
| Monitoring | Azure Monitor + Prometheus | Cloud Monitoring + Prometheus | Oracle Monitoring + Prometheus |

**Portability Strategy**:
- Use Kubernetes native resources (Deployment, Service, Ingress)
- Use Dapr for infrastructure abstractions (Kafka, Redis, Secrets)
- Use Helm for environment-specific configuration
- Avoid cloud-specific CRDs (Custom Resource Definitions)

### Risk Mitigation

- Test deployment on all three cloud platforms (CI/CD matrix)
- Document cloud-specific setup steps in quickstart.md
- Provide cost estimates for each cloud platform
- Use Terraform for cloud infrastructure provisioning (future enhancement)

---

## Decision 4: Full-Text Search Strategy

### Decision

**Selected**: PostgreSQL `tsvector` with GIN index

### Alternatives Considered

1. **PostgreSQL tsvector + GIN** ✅
   - Pros: Built-in, no extra service, good performance (<50ms), supports phrase search
   - Cons: Limited features vs Elasticsearch, no fuzzy matching, no typo tolerance
   - Complexity: Low (just add index + query function)

2. **Elasticsearch**
   - Pros: Best-in-class search, fuzzy matching, typo tolerance, relevance ranking
   - Cons: High complexity, extra service to manage, resource-heavy (1GB+ RAM)
   - Complexity: High (cluster management, index mapping, query DSL)

3. **Algolia / Typesense**
   - Pros: Excellent search UX, typo tolerance, instant results
   - Cons: Cost ($1/1000 searches), external dependency, vendor lock-in
   - Complexity: Medium (API integration, sync logic)

### Rationale

For Step 5's scope (search across task title and description):
- PostgreSQL full-text search is sufficient
- Avoids adding another service to manage
- <50ms latency for 10,000+ tasks
- Supports phrase search, stemming, ranking

**When to use Elasticsearch**:
- >100,000 tasks per user
- Need fuzzy matching / typo tolerance
- Complex search queries (filters, facets, aggregations)
- Search across multiple languages

### Implementation Notes

**Database Schema**:
```sql
-- Add tsvector column for full-text search
ALTER TABLE tasks ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
  ) STORED;

-- Create GIN index for fast search
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
```

**Query Example**:
```python
from sqlmodel import select, func

# Full-text search query
query = select(Task).where(
    func.to_tsquery("english", search_term).op("@@")(Task.search_vector)
)

# Ranked results
query = query.order_by(
    func.ts_rank(Task.search_vector, func.to_tsquery("english", search_term)).desc()
)
```

### Performance Benchmarks

- 1,000 tasks: ~5ms search latency
- 10,000 tasks: ~15ms search latency
- 100,000 tasks: ~50ms search latency

### Risk Mitigation

- Add search query caching (Redis) for common queries
- Limit search results to 100 items (paginate beyond)
- Sanitize search input to prevent SQL injection
- Monitor search query performance in production

---

## Decision 5: Reminder Processing Strategy

### Decision

**Selected**: Dapr Cron Binding (every 1 minute) with database queries

### Alternatives Considered

1. **Dapr Cron Binding + Database** ✅
   - Pros: Simple, reliable, predictable, no extra service
   - Cons: 1-minute granularity (60-second worst-case delay)
   - Complexity: Low (single cron job + database query)

2. **Celery Beat + Redis**
   - Pros: Precise scheduling, distributed task queue, retry logic
   - Cons: Adds Celery dependency, requires Redis, more complexity
   - Complexity: Medium (Celery worker, beat scheduler, Redis broker)

3. **Kubernetes CronJob**
   - Pros: Native Kubernetes, simple
   - Cons: Job overhead (create pod, run, delete), slower than in-process
   - Complexity: Low-Medium (CronJob YAML + job logic)

4. **APScheduler (in-process)**
   - Pros: Precise scheduling, no external dependencies
   - Cons: Not distributed (single instance), lost on pod restart
   - Complexity: Low (Python library)

### Rationale

Dapr Cron Binding meets requirements with minimal complexity:
- **60-second SLA**: Cron triggers every 1 minute, worst-case delay is 60 seconds
- **Reliability**: Dapr manages cron lifecycle, automatic retries
- **Scalability**: Stateless reminder processing (idempotent queries)
- **Simplicity**: No extra services, no distributed coordination

**Query Logic**:
```sql
SELECT * FROM reminders
WHERE reminder_at <= NOW()
  AND sent = false
ORDER BY reminder_at ASC
LIMIT 100;
```

**Idempotency**:
- Mark reminder as `sent=true` after publishing event
- Use database transaction to prevent duplicate sends
- Handle concurrent processing with optimistic locking

### Implementation Notes

**Cron Binding Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-reminder-processor
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/1 * * * *"  # Every 1 minute
```

**Reminder Processor**:
```python
@app.post("/cron")
async def process_reminders():
    # Query due reminders
    due_reminders = db.query(Reminder).filter(
        Reminder.reminder_at <= datetime.utcnow(),
        Reminder.sent == False
    ).limit(100).all()

    # Publish reminder.due events
    for reminder in due_reminders:
        publish_event("reminder.due", reminder)
        reminder.sent = True
        db.commit()
```

### Performance Considerations

- **Throughput**: Can process 100 reminders/minute (6,000/hour, 144,000/day)
- **Scaling**: If needed, reduce cron interval to 30 seconds (*/0.5 not supported, use two offset crons)
- **Monitoring**: Track reminder lag (time between reminder_at and actual send)

### Risk Mitigation

- Set reasonable reminder_offset limits (minimum 5 minutes, maximum 7 days)
- Monitor reminder processing lag and alert if >5 minutes
- Add retry logic for failed event publishes
- Implement rate limiting for reminder.due events (max 10/second)

---

## Decision 6: CI/CD Workflow Structure

### Decision

**Selected**: Separate CI and CD workflows

### Workflow Structure

**CI Workflow** (`.github/workflows/ci.yml`):
- Trigger: On pull request
- Steps:
  1. Run backend tests (pytest)
  2. Run frontend tests (npm test)
  3. Lint code (ruff, eslint)
  4. Type check (mypy, TypeScript)
  5. Build Docker images
  6. Security scan (Trivy)
  7. Helm chart validation (helm lint)

**CD Workflow** (`.github/workflows/cd.yml`):
- Trigger: On merge to main
- Steps:
  1. Build and push Docker images (with commit SHA tag)
  2. Deploy to cloud Kubernetes cluster (helm upgrade)
  3. Run smoke tests (health checks, critical flows)
  4. Rollback on failure (helm rollback)

### Rationale

Separating CI and CD provides:
- **Faster feedback**: CI runs on every PR, catches issues early
- **Clear separation**: CI = quality gates, CD = deployment automation
- **Better control**: CD only runs on main branch (protected)
- **Easier debugging**: Separate logs for test failures vs deployment issues

### Alternatives Considered

1. **Single combined workflow**
   - Pros: Simpler configuration
   - Cons: Harder to debug, slower PR feedback, less flexible

2. **GitOps (ArgoCD / FluxCD)**
   - Pros: Declarative, automatic sync, rollback history
   - Cons: Added complexity, extra service to manage, learning curve
   - Decision: Consider for Step 6+ (not Step 5)

### Implementation Notes

**CI Workflow Key Steps**:
```yaml
- name: Run backend tests
  run: |
    cd backend/api
    uv run pytest --cov=src --cov-report=xml

- name: Security scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_NAME }}
    format: 'sarif'
    output: 'trivy-results.sarif'
```

**CD Workflow Key Steps**:
```yaml
- name: Deploy to cloud
  run: |
    helm upgrade --install todo-app ./helm/todo-app \
      -f helm/todo-app/values-prod-${{ env.CLOUD_PROVIDER }}.yaml \
      --set backend.image.tag=${{ github.sha }} \
      --set frontend.image.tag=${{ github.sha }} \
      --set reminderService.image.tag=${{ github.sha }}

- name: Smoke tests
  run: |
    kubectl rollout status deployment/todo-app-backend
    curl -f http://${{ env.BACKEND_URL }}/health || exit 1
```

### Risk Mitigation

- Use GitHub Secrets for cloud credentials (never commit)
- Set up deployment environments (staging, production)
- Require PR approval before merge to main
- Implement blue-green deployment for zero downtime (future enhancement)

---

## Decision 7: Monitoring Stack Deployment

### Decision

**Selected**: In-cluster Prometheus + Grafana (for portability)

### Components

1. **Prometheus**: Metrics collection and storage
2. **Grafana**: Visualization and dashboards
3. **Zipkin or Jaeger**: Distributed tracing
4. **Loki**: Log aggregation (optional, can use cloud logging)
5. **Alertmanager**: Alert routing and notification

### Alternatives Considered

1. **In-Cluster Monitoring** ✅
   - Pros: Portable across clouds, full control, no vendor lock-in
   - Cons: Requires cluster resources, need to manage upgrades
   - Resource Usage: ~1GB RAM for full stack

2. **Cloud-Native Monitoring**
   - Azure Monitor, Cloud Monitoring, Oracle Monitoring
   - Pros: Fully managed, integrated with cloud services, auto-scaling
   - Cons: Vendor lock-in, higher cost, different APIs per cloud

3. **Datadog / New Relic**
   - Pros: Best-in-class UX, AI insights, extensive integrations
   - Cons: High cost ($15-30/host/month), vendor lock-in

### Rationale

In-cluster monitoring provides:
- **Portability**: Works on Minikube, AKS, GKE, OKE
- **Cost**: No per-host fees, just cluster resource costs
- **Control**: Full access to metrics, dashboards, alerts
- **Learning**: Developers understand monitoring stack

### Implementation Notes

**Prometheus Configuration**:
```yaml
# Scrape configs
scrape_configs:
  - job_name: 'backend'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: backend
        action: keep

  - job_name: 'reminder-service'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: reminder-service
        action: keep
```

**Grafana Dashboards**:
1. **Application Dashboard**: Request rate, latency, error rate, task operations
2. **Kubernetes Dashboard**: Pod health, resource usage, restarts
3. **Dapr Dashboard**: Pub/Sub throughput, state operations, service invocation
4. **Kafka Dashboard**: Consumer lag, throughput, broker health

**Alert Rules**:
- Error rate > 1% for 5 minutes
- p95 latency > 500ms for 5 minutes
- Kafka consumer lag > 1000 messages
- Pod restarts > 3 in 10 minutes

### Performance Impact

- Prometheus metrics collection: <1% CPU overhead per service
- Zipkin tracing (1% sampling): <0.1% CPU overhead
- Loki log aggregation: ~100MB RAM per service

### Risk Mitigation

- Set retention limits (Prometheus: 15 days, Loki: 7 days)
- Use persistent volumes for Prometheus data (prevent data loss on pod restart)
- Configure alert fatigue prevention (rate limiting, grouping)
- Document monitoring stack upgrade procedures

---

## Summary Table

| Decision | Selected Option | Key Trade-off |
|----------|-----------------|---------------|
| RRULE Parsing | python-dateutil | Complexity vs Correctness (chose Correctness) |
| Kafka Broker | Redpanda (dev), Confluent/Redpanda Cloud (prod) | Resource Usage vs Features (chose Lightweight) |
| Cloud Platform | Support all three (AKS, GKE, OKE) | Simplicity vs Portability (chose Portability) |
| Search | PostgreSQL tsvector + GIN | Simplicity vs Features (chose Simplicity) |
| Reminders | Dapr Cron Binding + Database | Precision vs Simplicity (chose Simplicity) |
| CI/CD | Separate workflows | Complexity vs Flexibility (chose Flexibility) |
| Monitoring | In-cluster Prometheus + Grafana | Cost vs Portability (chose Portability) |

---

## Future Decisions (Not in Step 5 Scope)

- **API Gateway**: Kong, Traefik, or Nginx Ingress Controller
- **Service Mesh**: Linkerd, Istio, or stick with Dapr
- **GitOps**: ArgoCD or FluxCD for declarative deployments
- **Cost Optimization**: Spot instances, auto-scaling, resource right-sizing
- **Disaster Recovery**: Multi-region deployment, backup strategies

---

## References

- python-dateutil: https://dateutil.readthedocs.io/
- Redpanda: https://redpanda.com/
- Confluent Cloud: https://www.confluent.io/confluent-cloud/
- PostgreSQL Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- Dapr Bindings: https://docs.dapr.io/developing-applications/building-blocks/bindings/
- GitHub Actions: https://docs.github.com/en/actions
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
