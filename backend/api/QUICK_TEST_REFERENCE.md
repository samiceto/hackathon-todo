# Quick Test Reference - Search, Filter, Sort

**Copy-paste these commands to quickly test Phase 6 features**

## Setup
```bash
# Terminal 1: Start backend
cd backend/api
uvicorn src.main:app --reload

# Terminal 2: Run tests
# Replace YOUR_JWT_TOKEN with actual token
export TOKEN="YOUR_JWT_TOKEN"
```

## Quick Tests (Copy & Paste)

### 1. Search
```bash
# Search for "meeting"
curl "http://localhost:8000/api/1/tasks?search=meeting" -H "Authorization: Bearer $TOKEN"

# Search for "team project" (multi-word)
curl "http://localhost:8000/api/1/tasks?search=team+project" -H "Authorization: Bearer $TOKEN"
```

### 2. Filter by Status
```bash
# Incomplete tasks only
curl "http://localhost:8000/api/1/tasks?status=incomplete" -H "Authorization: Bearer $TOKEN"

# Completed tasks only
curl "http://localhost:8000/api/1/tasks?status=completed" -H "Authorization: Bearer $TOKEN"
```

### 3. Filter by Priority
```bash
# High priority tasks
curl "http://localhost:8000/api/1/tasks?priority=high" -H "Authorization: Bearer $TOKEN"

# Urgent tasks
curl "http://localhost:8000/api/1/tasks?priority=urgent" -H "Authorization: Bearer $TOKEN"
```

### 4. Filter by Tags
```bash
# Single tag
curl "http://localhost:8000/api/1/tasks?tags=work" -H "Authorization: Bearer $TOKEN"

# Multiple tags (AND logic)
curl "http://localhost:8000/api/1/tasks?tags=urgent&tags=meeting" -H "Authorization: Bearer $TOKEN"
```

### 5. Filter by Due Date
```bash
# Tasks due today or later
curl "http://localhost:8000/api/1/tasks?due_date_start=$(date -u +%Y-%m-%dT%H:%M:%S)" -H "Authorization: Bearer $TOKEN"

# Tasks due this week
curl "http://localhost:8000/api/1/tasks?due_date_start=$(date -u +%Y-%m-%dT00:00:00)&due_date_end=$(date -u -d '+7 days' +%Y-%m-%dT23:59:59)" -H "Authorization: Bearer $TOKEN"
```

### 6. Sort
```bash
# Sort by due date (soonest first)
curl "http://localhost:8000/api/1/tasks?sort_by=due_date&sort_order=asc" -H "Authorization: Bearer $TOKEN"

# Sort by priority (urgent first)
curl "http://localhost:8000/api/1/tasks?sort_by=priority&sort_order=desc" -H "Authorization: Bearer $TOKEN"

# Sort by title (A-Z)
curl "http://localhost:8000/api/1/tasks?sort_by=title&sort_order=asc" -H "Authorization: Bearer $TOKEN"
```

### 7. Combined (Filter + Sort)
```bash
# Incomplete high-priority tasks, sorted by due date
curl "http://localhost:8000/api/1/tasks?status=incomplete&priority=high&sort_by=due_date&sort_order=asc" -H "Authorization: Bearer $TOKEN"

# Urgent tasks with "work" tag, newest first
curl "http://localhost:8000/api/1/tasks?priority=urgent&tags=work&sort_by=created_at&sort_order=desc" -H "Authorization: Bearer $TOKEN"
```

### 8. Pagination
```bash
# First 5 tasks
curl "http://localhost:8000/api/1/tasks?limit=5" -H "Authorization: Bearer $TOKEN"

# Page 2 (next 10 tasks)
curl "http://localhost:8000/api/1/tasks?limit=10&offset=10" -H "Authorization: Bearer $TOKEN"
```

### 9. Pretty Print (with jq)
```bash
# Install jq: sudo apt install jq (Linux) or brew install jq (Mac)

# Search with pretty output
curl -s "http://localhost:8000/api/1/tasks?search=meeting" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Filter with pretty output
curl -s "http://localhost:8000/api/1/tasks?status=incomplete&priority=high" \
  -H "Authorization: Bearer $TOKEN" | jq '.tasks[] | {id, title, priority, completed}'
```

## Frontend Quick Test

```bash
# Terminal 3: Start frontend
cd frontend
npm run dev

# Open browser: http://localhost:3000/tasks
```

**Test Checklist**:
- [ ] Type "meeting" in search bar → see filtered results
- [ ] Change Status filter to "Incomplete" → see only incomplete tasks
- [ ] Change Priority filter to "High" → see only high priority tasks
- [ ] Enter tags "urgent, work" → see tasks with both tags
- [ ] Change Sort to "Due Date (Ascending)" → see tasks sorted by deadline
- [ ] Click "Clear all" → see all tasks again

## Expected Response Format

```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Team meeting",
      "description": "Discuss project progress",
      "completed": false,
      "priority": "high",
      "due_date": "2026-02-01T14:00:00",
      "tags": ["urgent", "meeting"],
      "created_at": "2026-01-30T10:00:00",
      "updated_at": "2026-01-30T10:00:00"
    }
  ],
  "total": 1
}
```

## Common Errors and Fixes

### 401 Unauthorized
**Fix**: Update TOKEN variable with valid JWT

### 400 Bad Request
**Fix**: Check query parameter names and values
- Valid status: "completed" or "incomplete"
- Valid priority: "low", "medium", "high", "urgent"
- Valid sort_by: "created_at", "updated_at", "due_date", "priority", "title"
- Valid sort_order: "asc" or "desc"

### Empty results
**Fix**: Create test data first
```bash
# Create a test task via API
curl -X POST "http://localhost:8000/api/1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task for search",
    "description": "Meeting notes for team project",
    "priority": "high",
    "due_date": "2026-02-01T14:00:00"
  }'

# Add tags to the task (task_id=1 example)
curl -X POST "http://localhost:8000/api/1/tasks/1/tags" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "urgent"}'
```

## Performance Test

```bash
# Test with pagination (100 tasks per page)
for i in {0..9}; do
  echo "Page $((i+1)):"
  curl -s "http://localhost:8000/api/1/tasks?limit=100&offset=$((i*100))" \
    -H "Authorization: Bearer $TOKEN" | jq '.total'
done
```

## Success Criteria

✅ **All tests pass when**:
1. Search returns relevant results
2. Filters return only matching tasks
3. Sort orders results correctly
4. Pagination works for large datasets
5. Error handling is clear and helpful
6. Frontend UI is responsive and intuitive

---

**Quick Link**: Full test guide at `backend/api/MANUAL_TEST_GUIDE.md`
