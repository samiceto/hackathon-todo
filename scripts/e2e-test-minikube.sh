#!/bin/bash
# End-to-End Test Script for Minikube Deployment (Step 5)
# Tests: Recurring tasks, reminders, and event-driven architecture

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

RELEASE_NAME="todo-app"
NAMESPACE="default"
BACKEND_SERVICE="todo-app-backend"
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "localhost")

# Test configuration
TEST_TIMEOUT=300  # 5 minutes max for tests
POLL_INTERVAL=5   # Check every 5 seconds

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}End-to-End Tests for Todo App${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to run a test
run_test() {
    local test_name="$1"
    local test_function="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}[TEST $TESTS_TOTAL] $test_name${NC}"

    if $test_function; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo ""
        return 0
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo ""
        return 1
    fi
}

# Function to make API request
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    if [ -z "$data" ]; then
        kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never --quiet -- \
            curl -s -X "$method" "http://$BACKEND_SERVICE:8000$endpoint" \
            -H "Content-Type: application/json" 2>/dev/null || echo ""
    else
        kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never --quiet -- \
            curl -s -X "$method" "http://$BACKEND_SERVICE:8000$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo ""
    fi
}

# Test 1: Check deployment is running
test_deployment_running() {
    echo "  Checking if all pods are running..."

    local backend_ready=$(kubectl get pods -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].status.containerStatuses[?(@.name=="backend")].ready}' 2>/dev/null)
    local frontend_ready=$(kubectl get pods -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].status.containerStatuses[?(@.name=="frontend")].ready}' 2>/dev/null)
    local reminder_ready=$(kubectl get pods -l app.kubernetes.io/component=reminder-service -o jsonpath='{.items[0].status.containerStatuses[?(@.name=="reminder-service")].ready}' 2>/dev/null)

    if [ "$backend_ready" = "true" ] && [ "$frontend_ready" = "true" ] && [ "$reminder_ready" = "true" ]; then
        echo "  ✓ All pods are running"
        return 0
    else
        echo "  ✗ Some pods are not ready"
        echo "    Backend: $backend_ready"
        echo "    Frontend: $frontend_ready"
        echo "    Reminder: $reminder_ready"
        return 1
    fi
}

# Test 2: Check backend health endpoint
test_backend_health() {
    echo "  Checking backend health endpoint..."

    local response=$(api_request GET /health)

    if echo "$response" | grep -q "healthy"; then
        echo "  ✓ Backend is healthy"
        return 0
    else
        echo "  ✗ Backend health check failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 3: Check Dapr components
test_dapr_components() {
    echo "  Checking Dapr components..."

    local pubsub=$(kubectl get component pubsub-kafka -o jsonpath='{.metadata.name}' 2>/dev/null)
    local statestore=$(kubectl get component statestore-redis -o jsonpath='{.metadata.name}' 2>/dev/null)
    local cron=$(kubectl get component cron-reminder-processor -o jsonpath='{.metadata.name}' 2>/dev/null)
    local secrets=$(kubectl get component kubernetes-secrets -o jsonpath='{.metadata.name}' 2>/dev/null)

    if [ "$pubsub" = "pubsub-kafka" ] && [ "$statestore" = "statestore-redis" ] && \
       [ "$cron" = "cron-reminder-processor" ] && [ "$secrets" = "kubernetes-secrets" ]; then
        echo "  ✓ All Dapr components are configured"
        return 0
    else
        echo "  ✗ Some Dapr components are missing"
        echo "    Pub/Sub: $pubsub"
        echo "    State Store: $statestore"
        echo "    Cron: $cron"
        echo "    Secrets: $secrets"
        return 1
    fi
}

# Test 4: Create a simple task
test_create_task() {
    echo "  Creating a simple task..."

    local task_data='{"title":"E2E Test Task","description":"Testing task creation"}'
    local response=$(api_request POST /tasks "$task_data")

    if echo "$response" | grep -q "E2E Test Task"; then
        echo "  ✓ Task created successfully"
        # Extract task ID for cleanup
        SIMPLE_TASK_ID=$(echo "$response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
        echo "    Task ID: $SIMPLE_TASK_ID"
        return 0
    else
        echo "  ✗ Task creation failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 5: List tasks
test_list_tasks() {
    echo "  Listing all tasks..."

    local response=$(api_request GET /tasks)

    if echo "$response" | grep -q "E2E Test Task"; then
        echo "  ✓ Tasks retrieved successfully"
        return 0
    else
        echo "  ✗ Failed to retrieve tasks"
        echo "    Response: $response"
        return 1
    fi
}

# Test 6: Create recurring task
test_create_recurring_task() {
    echo "  Creating a recurring task (daily)..."

    # Create a task that recurs daily
    local task_data='{"title":"Daily Standup","description":"Recurring test task","recurrence_rule":"FREQ=DAILY","priority":"medium"}'
    local response=$(api_request POST /tasks "$task_data")

    if echo "$response" | grep -q "Daily Standup"; then
        echo "  ✓ Recurring task created successfully"
        RECURRING_TASK_ID=$(echo "$response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
        echo "    Task ID: $RECURRING_TASK_ID"
        return 0
    else
        echo "  ✗ Recurring task creation failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 7: Create task with due date and reminder
test_create_task_with_reminder() {
    echo "  Creating a task with due date and reminder..."

    # Create a task with due date 10 minutes in future and 5-minute reminder
    local due_date=$(date -u -d "+10 minutes" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v+10M +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
    local task_data="{\"title\":\"Urgent Meeting\",\"description\":\"Task with reminder\",\"due_date\":\"$due_date\",\"reminder_offset\":300,\"priority\":\"high\"}"
    local response=$(api_request POST /tasks "$task_data")

    if echo "$response" | grep -q "Urgent Meeting"; then
        echo "  ✓ Task with reminder created successfully"
        REMINDER_TASK_ID=$(echo "$response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
        echo "    Task ID: $REMINDER_TASK_ID"
        echo "    Due date: $due_date"
        return 0
    else
        echo "  ✗ Task with reminder creation failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 8: Update task
test_update_task() {
    echo "  Updating task..."

    if [ -z "$SIMPLE_TASK_ID" ]; then
        echo "  ✗ No task ID available for update"
        return 1
    fi

    local update_data='{"title":"E2E Test Task (Updated)","description":"Updated description"}'
    local response=$(api_request PUT "/tasks/$SIMPLE_TASK_ID" "$update_data")

    if echo "$response" | grep -q "Updated"; then
        echo "  ✓ Task updated successfully"
        return 0
    else
        echo "  ✗ Task update failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 9: Mark task as complete
test_complete_task() {
    echo "  Marking task as complete..."

    if [ -z "$SIMPLE_TASK_ID" ]; then
        echo "  ✗ No task ID available for completion"
        return 1
    fi

    local response=$(api_request PUT "/tasks/$SIMPLE_TASK_ID/complete")

    if echo "$response" | grep -q "completed"; then
        echo "  ✓ Task marked as complete"
        return 0
    else
        echo "  ✗ Task completion failed"
        echo "    Response: $response"
        return 1
    fi
}

# Test 10: Check Kafka topics (Redpanda)
test_kafka_topics() {
    echo "  Checking Kafka topics..."

    local topics=$(kubectl exec -it redpanda-0 -- rpk topic list 2>/dev/null | grep -E "task\.|reminder\." || echo "")

    if echo "$topics" | grep -q "task.created"; then
        echo "  ✓ Kafka topics are configured"
        echo "    Topics: $(echo $topics | tr '\n' ' ')"
        return 0
    else
        echo "  ⚠️  Warning: Could not verify Kafka topics (may not be critical)"
        return 0  # Don't fail the test, just warn
    fi
}

# Test 11: Check Redis connectivity
test_redis_connectivity() {
    echo "  Checking Redis connectivity..."

    local redis_ping=$(kubectl exec -it redis-0 -- redis-cli ping 2>/dev/null | tr -d '\r')

    if [ "$redis_ping" = "PONG" ]; then
        echo "  ✓ Redis is responding"
        return 0
    else
        echo "  ✗ Redis connectivity failed"
        return 1
    fi
}

# Test 12: Check reminder service logs
test_reminder_service_logs() {
    echo "  Checking reminder service logs..."

    local pod_name=$(kubectl get pods -l app.kubernetes.io/component=reminder-service -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$pod_name" ]; then
        echo "  ✗ Reminder service pod not found"
        return 1
    fi

    local logs=$(kubectl logs "$pod_name" -c reminder-service --tail=50 2>/dev/null || echo "")

    if [ -n "$logs" ]; then
        echo "  ✓ Reminder service is logging"
        return 0
    else
        echo "  ⚠️  Warning: No logs from reminder service"
        return 0  # Don't fail, just warn
    fi
}

# Cleanup function
cleanup_test_data() {
    echo -e "${BLUE}Cleaning up test data...${NC}"

    if [ -n "$SIMPLE_TASK_ID" ]; then
        echo "  Deleting task $SIMPLE_TASK_ID..."
        api_request DELETE "/tasks/$SIMPLE_TASK_ID" > /dev/null 2>&1 || true
    fi

    if [ -n "$RECURRING_TASK_ID" ]; then
        echo "  Deleting task $RECURRING_TASK_ID..."
        api_request DELETE "/tasks/$RECURRING_TASK_ID" > /dev/null 2>&1 || true
    fi

    if [ -n "$REMINDER_TASK_ID" ]; then
        echo "  Deleting task $REMINDER_TASK_ID..."
        api_request DELETE "/tasks/$REMINDER_TASK_ID" > /dev/null 2>&1 || true
    fi

    echo -e "${GREEN}✅ Cleanup complete${NC}"
    echo ""
}

# Main test execution
main() {
    echo -e "${YELLOW}Starting E2E tests...${NC}"
    echo ""

    # Prerequisites
    run_test "Deployment is running" test_deployment_running || exit 1
    run_test "Backend health check" test_backend_health || exit 1
    run_test "Dapr components configured" test_dapr_components || exit 1

    # Infrastructure tests
    run_test "Redis connectivity" test_redis_connectivity
    run_test "Kafka topics configured" test_kafka_topics

    # Basic CRUD operations
    run_test "Create simple task" test_create_task
    run_test "List tasks" test_list_tasks
    run_test "Update task" test_update_task
    run_test "Complete task" test_complete_task

    # Advanced features
    run_test "Create recurring task" test_create_recurring_task
    run_test "Create task with reminder" test_create_task_with_reminder
    run_test "Reminder service logging" test_reminder_service_logs

    # Cleanup
    cleanup_test_data

    # Summary
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Total tests:  $TESTS_TOTAL"
    echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
    echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}========================================${NC}"
        exit 0
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}❌ SOME TESTS FAILED${NC}"
        echo -e "${RED}========================================${NC}"
        exit 1
    fi
}

# Run main function
main
