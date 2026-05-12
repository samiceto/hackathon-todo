# Performance Optimization Checklist - Step 5

**Step 5: Advanced Cloud Deployment - Performance Best Practices**

Use this checklist to optimize the performance of your Todo App deployment on Minikube or AWS k3s.

---

## Database Optimization

### Query Optimization

- [ ] **Add database indexes for frequently queried fields**
  ```sql
  -- Already implemented in migration 004
  CREATE INDEX idx_tasks_user_id ON tasks(user_id);
  CREATE INDEX idx_tasks_completed ON tasks(completed);
  CREATE INDEX idx_tasks_due_date ON tasks(due_date);
  CREATE INDEX idx_reminders_reminder_at ON reminders(reminder_at, sent);

  -- Full-text search index
  CREATE INDEX idx_tasks_search ON tasks USING GIN(to_tsvector('english', title || ' ' || description));
  ```

- [ ] **Use query explain to identify slow queries**
  ```sql
  EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 1 AND completed = false;
  ```

- [ ] **Optimize N+1 queries with eager loading**
  ```python
  # Bad: N+1 query
  tasks = session.exec(select(Task)).all()
  for task in tasks:
      tags = task.tags  # Separate query for each task

  # Good: Eager loading
  from sqlmodel import select
  from sqlalchemy.orm import selectinload

  tasks = session.exec(
      select(Task).options(selectinload(Task.tags))
  ).all()
  ```

- [ ] **Use pagination for large result sets**
  ```python
  # Limit results per page
  tasks = session.exec(
      select(Task).offset(skip).limit(limit)
  ).all()
  ```

- [ ] **Add connection pooling configuration**
  ```python
  # In database.py
  engine = create_engine(
      DATABASE_URL,
      pool_size=10,
      max_overflow=20,
      pool_pre_ping=True,
      pool_recycle=3600
  )
  ```

### Database Monitoring

- [ ] **Enable query logging for slow queries**
  ```python
  # In config
  LOG_SLOW_QUERIES = True
  SLOW_QUERY_THRESHOLD = 1.0  # seconds
  ```

- [ ] **Monitor database connection pool usage**
  ```python
  # Add metrics endpoint
  @app.get("/metrics/db")
  def db_metrics():
      return {
          "pool_size": engine.pool.size(),
          "checked_in": engine.pool.checkedin(),
          "checked_out": engine.pool.checkedout(),
          "overflow": engine.pool.overflow()
      }
  ```

- [ ] **Set up database performance monitoring**
  - Use Neon dashboard for query analytics
  - Monitor connection count
  - Track query execution times

---

## Caching Strategies

### Redis Caching

- [ ] **Cache frequently accessed data**
  ```python
  from redis import Redis
  import json

  redis_client = Redis(host='redis', port=6379, decode_responses=True)

  def get_task_cached(task_id: int):
      # Try cache first
      cached = redis_client.get(f"task:{task_id}")
      if cached:
          return json.loads(cached)

      # Fetch from database
      task = session.get(Task, task_id)

      # Cache for 5 minutes
      redis_client.setex(
          f"task:{task_id}",
          300,
          json.dumps(task.dict())
      )
      return task
  ```

- [ ] **Implement cache invalidation on updates**
  ```python
  def update_task(task_id: int, data: dict):
      task = session.get(Task, task_id)
      # Update task...
      session.commit()

      # Invalidate cache
      redis_client.delete(f"task:{task_id}")
  ```

- [ ] **Cache search results**
  ```python
  def search_tasks_cached(query: str):
      cache_key = f"search:{query}"
      cached = redis_client.get(cache_key)
      if cached:
          return json.loads(cached)

      results = search_tasks(query)
      redis_client.setex(cache_key, 60, json.dumps(results))
      return results
  ```

### HTTP Caching

- [ ] **Add Cache-Control headers for static assets**
  ```python
  @app.get("/static/{file_path:path}")
  def serve_static(file_path: str):
      return FileResponse(
          f"static/{file_path}",
          headers={"Cache-Control": "public, max-age=31536000"}
      )
  ```

- [ ] **Implement ETag for API responses**
  ```python
  from hashlib import md5

  @app.get("/tasks")
  def get_tasks(request: Request):
      tasks = fetch_tasks()
      content = json.dumps(tasks)
      etag = md5(content.encode()).hexdigest()

      if request.headers.get("If-None-Match") == etag:
          return Response(status_code=304)

      return Response(
          content=content,
          headers={"ETag": etag}
      )
  ```

---

## Application Performance

### FastAPI Optimization

- [ ] **Enable async database operations**
  ```python
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

  async_engine = create_async_engine(DATABASE_URL)

  @app.get("/tasks")
  async def get_tasks():
      async with AsyncSession(async_engine) as session:
          result = await session.execute(select(Task))
          return result.scalars().all()
  ```

- [ ] **Use background tasks for non-blocking operations**
  ```python
  from fastapi import BackgroundTasks

  @app.post("/tasks")
  def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
      # Create task synchronously
      new_task = Task(**task.dict())
      session.add(new_task)
      session.commit()

      # Publish event asynchronously
      background_tasks.add_task(publish_event, "task.created", new_task)

      return new_task
  ```

- [ ] **Optimize JSON serialization**
  ```python
  from fastapi.responses import ORJSONResponse

  app = FastAPI(default_response_class=ORJSONResponse)
  ```

- [ ] **Enable compression**
  ```python
  from fastapi.middleware.gzip import GZipMiddleware

  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```

### Frontend Optimization

- [ ] **Enable Next.js production optimizations**
  ```bash
  # Build with optimizations
  npm run build

  # Verify bundle size
  npm run analyze
  ```

- [ ] **Implement code splitting**
  ```typescript
  // Use dynamic imports
  const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
    loading: () => <p>Loading...</p>
  })
  ```

- [ ] **Optimize images**
  ```typescript
  import Image from 'next/image'

  <Image
    src="/logo.png"
    width={200}
    height={100}
    alt="Logo"
    priority
  />
  ```

- [ ] **Add service worker for offline support**
  ```typescript
  // next.config.js
  const withPWA = require('next-pwa')

  module.exports = withPWA({
    pwa: {
      dest: 'public',
      register: true,
      skipWaiting: true
    }
  })
  ```

---

## Kubernetes Resource Optimization

### Pod Resources

- [ ] **Right-size resource requests and limits**
  ```bash
  # Monitor actual usage
  kubectl top pods -l app.kubernetes.io/instance=todo-app

  # Adjust in values.yaml based on actual usage
  backend:
    resources:
      requests:
        cpu: "250m"      # Set to 80% of average usage
        memory: "256Mi"
      limits:
        cpu: "500m"      # Set to 2x requests
        memory: "512Mi"  # Set to handle spikes
  ```

- [ ] **Enable Horizontal Pod Autoscaling (HPA)**
  ```yaml
  # In values.yaml
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  ```

- [ ] **Configure Pod Disruption Budget**
  ```yaml
  podDisruptionBudget:
    enabled: true
    minAvailable: 1
  ```

### Node Optimization

- [ ] **Use node affinity for workload placement**
  ```yaml
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: workload-type
            operator: In
            values:
            - compute-optimized
  ```

- [ ] **Enable cluster autoscaling (cloud only)**
  ```bash
  # AWS
  aws eks update-nodegroup-config \
    --cluster-name todo-app \
    --nodegroup-name workers \
    --scaling-config minSize=2,maxSize=10,desiredSize=3
  ```

---

## Event-Driven Architecture Optimization

### Kafka/Redpanda Performance

- [ ] **Optimize topic partitions**
  ```bash
  # Increase partitions for high-throughput topics
  kubectl exec -it redpanda-0 -- \
    rpk topic alter-config task.created --set partition.count=3
  ```

- [ ] **Configure producer batching**
  ```python
  # In Dapr pubsub metadata
  metadata:
    - name: producerBatchSize
      value: "100"
    - name: producerBatchMaxBytes
      value: "1048576"
  ```

- [ ] **Enable compression**
  ```python
  metadata:
    - name: compressionType
      value: "snappy"
  ```

- [ ] **Monitor consumer lag**
  ```bash
  kubectl exec -it redpanda-0 -- \
    rpk group describe todo-app-group
  ```

### Dapr Optimization

- [ ] **Configure Dapr sidecar resources**
  ```yaml
  annotations:
    dapr.io/sidecar-cpu-limit: "200m"
    dapr.io/sidecar-memory-limit: "256Mi"
    dapr.io/sidecar-cpu-request: "100m"
    dapr.io/sidecar-memory-request: "128Mi"
  ```

- [ ] **Enable Dapr metrics**
  ```yaml
  annotations:
    dapr.io/enable-metrics: "true"
    dapr.io/metrics-port: "9090"
  ```

- [ ] **Optimize state store operations**
  ```python
  # Use bulk operations
  await dapr_client.save_bulk_state(
      store_name="statestore-redis",
      states=[
          StateItem(key="key1", value="value1"),
          StateItem(key="key2", value="value2")
      ]
  )
  ```

---

## Monitoring and Profiling

### Application Profiling

- [ ] **Add performance logging**
  ```python
  import time
  from functools import wraps

  def log_performance(func):
      @wraps(func)
      def wrapper(*args, **kwargs):
          start = time.time()
          result = func(*args, **kwargs)
          duration = time.time() - start
          logger.info(f"{func.__name__} took {duration:.2f}s")
          return result
      return wrapper
  ```

- [ ] **Use Python profiler for bottlenecks**
  ```python
  import cProfile
  import pstats

  profiler = cProfile.Profile()
  profiler.enable()

  # Run code to profile

  profiler.disable()
  stats = pstats.Stats(profiler)
  stats.sort_stats('cumulative')
  stats.print_stats(10)
  ```

### Metrics Collection

- [ ] **Expose Prometheus metrics**
  ```python
  from prometheus_client import Counter, Histogram, generate_latest

  request_count = Counter('http_requests_total', 'Total HTTP requests')
  request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

  @app.get("/metrics")
  def metrics():
      return Response(generate_latest(), media_type="text/plain")
  ```

- [ ] **Monitor key performance indicators**
  - API response time (p50, p95, p99)
  - Database query time
  - Event processing latency
  - Cache hit rate
  - Error rate

---

## Load Testing

### Performance Benchmarks

- [ ] **Run load tests with realistic traffic**
  ```bash
  # Install k6
  brew install k6

  # Create load test script
  cat > load-test.js <<EOF
  import http from 'k6/http';
  import { check, sleep } from 'k6';

  export let options = {
    stages: [
      { duration: '2m', target: 100 },  // Ramp up
      { duration: '5m', target: 100 },  // Stay at 100 users
      { duration: '2m', target: 0 },    // Ramp down
    ],
  };

  export default function () {
    let res = http.get('http://backend:8000/tasks');
    check(res, { 'status is 200': (r) => r.status === 200 });
    sleep(1);
  }
  EOF

  # Run test
  k6 run load-test.js
  ```

- [ ] **Establish performance baselines**
  - Target: API response time < 200ms (p95)
  - Target: Database query time < 50ms (p95)
  - Target: Event processing latency < 1s
  - Target: Throughput > 100 req/s

- [ ] **Test under stress conditions**
  ```bash
  # Stress test with 1000 concurrent users
  k6 run --vus 1000 --duration 30s load-test.js
  ```

---

## Performance Checklist Summary

**Database** (5/5):
- [ ] Indexes on frequently queried fields
- [ ] Query optimization with EXPLAIN
- [ ] Connection pooling configured
- [ ] Pagination for large results
- [ ] Slow query monitoring

**Caching** (3/3):
- [ ] Redis caching for hot data
- [ ] Cache invalidation strategy
- [ ] HTTP caching headers

**Application** (4/4):
- [ ] Async operations where possible
- [ ] Background tasks for non-blocking work
- [ ] Response compression enabled
- [ ] JSON serialization optimized

**Kubernetes** (3/3):
- [ ] Resource requests/limits right-sized
- [ ] HPA configured (if needed)
- [ ] Pod disruption budget set

**Event-Driven** (3/3):
- [ ] Kafka partitions optimized
- [ ] Producer batching enabled
- [ ] Consumer lag monitored

**Monitoring** (3/3):
- [ ] Prometheus metrics exposed
- [ ] Performance logging added
- [ ] Load testing completed

---

**Last Updated**: 2026-02-09
**Version**: Step 5 - Performance Optimization Checklist
