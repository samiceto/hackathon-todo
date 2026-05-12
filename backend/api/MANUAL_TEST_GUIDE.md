# Manual Testing Guide: Search, Filter, and Sort Features

**Phase 6 - User Story 4**
**Date**: 2026-01-30
**Status**: Ready for Testing

## Prerequisites

1. **Backend Running**:
   ```bash
   cd backend/api
   uvicorn src.main:app --reload
   ```
   Backend should be running at: http://localhost:8000

2. **Have Test Data**: Create some tasks with varied properties:
   - Different titles and descriptions
   - Various priority levels (low, medium, high, urgent)
   - Different completion statuses
   - Multiple tags per task
   - Various due dates

3. **Authentication**: Get a valid JWT token for user_id=1

## Test 1: Search Functionality

### 1.1 Basic Search - Single Word
```bash
curl "http://localhost:8000/api/1/tasks?search=meeting" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks with "meeting" in title OR description
- Results ordered by relevance (ts_rank)
- JSON response with `tasks` array and `total` count

**Verify**:
- [ ] Tasks containing "meeting" are returned
- [ ] Tasks without "meeting" are NOT returned
- [ ] Relevance ranking works (title matches ranked higher)

### 1.2 Multi-Word Search
```bash
curl "http://localhost:8000/api/1/tasks?search=team+project" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks containing "team" OR "project"
- Uses OR logic between words

**Verify**:
- [ ] Tasks with either word are returned
- [ ] Tasks with both words ranked higher

### 1.3 Case-Insensitive Search
```bash
curl "http://localhost:8000/api/1/tasks?search=URGENT" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks with "urgent", "URGENT", "Urgent", etc.
- Case doesn't matter

**Verify**:
- [ ] Case-insensitive matching works

### 1.4 Empty Search
```bash
curl "http://localhost:8000/api/1/tasks?search=" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns empty list (no search performed)
- Or returns all tasks (depends on implementation)

**Verify**:
- [ ] Empty query handled gracefully

---

## Test 2: Filter Functionality

### 2.1 Filter by Status - Incomplete Only
```bash
curl "http://localhost:8000/api/1/tasks?status=incomplete" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns only tasks where `completed = false`

**Verify**:
- [ ] All returned tasks have `"completed": false`
- [ ] Completed tasks are excluded

### 2.2 Filter by Status - Completed Only
```bash
curl "http://localhost:8000/api/1/tasks?status=completed" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns only tasks where `completed = true`

**Verify**:
- [ ] All returned tasks have `"completed": true`
- [ ] Incomplete tasks are excluded

### 2.3 Filter by Priority - High Priority
```bash
curl "http://localhost:8000/api/1/tasks?priority=high" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns only tasks with priority = "high"

**Verify**:
- [ ] All returned tasks have `"priority": "high"`
- [ ] Tasks with other priorities are excluded

### 2.4 Filter by Multiple Criteria (Status + Priority)
```bash
curl "http://localhost:8000/api/1/tasks?status=incomplete&priority=urgent" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks that are BOTH incomplete AND urgent priority
- Uses AND logic

**Verify**:
- [ ] All tasks have `"completed": false` AND `"priority": "urgent"`
- [ ] Tasks missing either criterion are excluded

### 2.5 Filter by Tags - Single Tag
```bash
curl "http://localhost:8000/api/1/tasks?tags=work" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks that have the tag "work"

**Verify**:
- [ ] All returned tasks contain "work" in their tags array
- [ ] Tasks without the tag are excluded

### 2.6 Filter by Tags - Multiple Tags (AND Logic)
```bash
curl "http://localhost:8000/api/1/tasks?tags=urgent&tags=meeting" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks that have BOTH "urgent" AND "meeting" tags
- Uses AND logic for tags

**Verify**:
- [ ] All returned tasks have BOTH tags
- [ ] Tasks with only one tag are excluded

### 2.7 Filter by Due Date Range - Start Date
```bash
curl "http://localhost:8000/api/1/tasks?due_date_start=2026-01-30T00:00:00" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks with due_date >= 2026-01-30

**Verify**:
- [ ] All tasks have due_date on or after Jan 30, 2026
- [ ] Earlier tasks are excluded

### 2.8 Filter by Due Date Range - Start and End
```bash
curl "http://localhost:8000/api/1/tasks?due_date_start=2026-02-01T00:00:00&due_date_end=2026-02-07T23:59:59" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks due between Feb 1 and Feb 7, 2026

**Verify**:
- [ ] All tasks have due_date within range
- [ ] Tasks outside range are excluded

### 2.9 Complex Filter - All Criteria
```bash
curl "http://localhost:8000/api/1/tasks?status=incomplete&priority=high&tags=urgent&due_date_start=2026-01-30T00:00:00" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns tasks matching ALL criteria
- Incomplete + High Priority + Has "urgent" tag + Due on/after Jan 30

**Verify**:
- [ ] All returned tasks satisfy ALL conditions
- [ ] Any task missing one criterion is excluded

---

## Test 3: Sort Functionality

### 3.1 Sort by Created Date (Newest First)
```bash
curl "http://localhost:8000/api/1/tasks?sort_by=created_at&sort_order=desc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Tasks ordered by creation date, newest first

**Verify**:
- [ ] First task has most recent created_at
- [ ] Last task has oldest created_at
- [ ] Order is descending

### 3.2 Sort by Due Date (Soonest First)
```bash
curl "http://localhost:8000/api/1/tasks?sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Tasks ordered by due date, soonest deadlines first

**Verify**:
- [ ] First task has earliest due_date
- [ ] Last task has latest due_date
- [ ] Order is ascending

### 3.3 Sort by Priority (Descending)
```bash
curl "http://localhost:8000/api/1/tasks?sort_by=priority&sort_order=desc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Tasks ordered: urgent → high → medium → low

**Verify**:
- [ ] Urgent tasks appear first
- [ ] Low priority tasks appear last
- [ ] Priority order is correct

### 3.4 Sort by Title (Alphabetical)
```bash
curl "http://localhost:8000/api/1/tasks?sort_by=title&sort_order=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Tasks ordered alphabetically by title (A→Z)

**Verify**:
- [ ] Titles are in alphabetical order
- [ ] Case-insensitive sorting

### 3.5 Combined Filter + Sort
```bash
curl "http://localhost:8000/api/1/tasks?status=incomplete&priority=high&sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Filters for incomplete high-priority tasks
- Then sorts by due date (soonest first)

**Verify**:
- [ ] All tasks are incomplete and high priority
- [ ] Results are sorted by due date ascending

---

## Test 4: Pagination

### 4.1 Limit Results
```bash
curl "http://localhost:8000/api/1/tasks?limit=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- Returns maximum 5 tasks

**Verify**:
- [ ] Response has at most 5 tasks
- [ ] `total` field shows actual count

### 4.2 Offset + Limit (Pagination)
```bash
# Page 1 (first 10 tasks)
curl "http://localhost:8000/api/1/tasks?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Page 2 (next 10 tasks)
curl "http://localhost:8000/api/1/tasks?limit=10&offset=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- First request returns tasks 1-10
- Second request returns tasks 11-20

**Verify**:
- [ ] Different tasks in each response
- [ ] No overlap between pages

---

## Test 5: Error Handling

### 5.1 Invalid Status Value
```bash
curl "http://localhost:8000/api/1/tasks?status=invalid" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- 400 Bad Request
- Error message: "Invalid filter parameters: Invalid status: invalid..."

**Verify**:
- [ ] Returns 400 status code
- [ ] Error message is clear and helpful

### 5.2 Invalid Priority Value
```bash
curl "http://localhost:8000/api/1/tasks?priority=super-urgent" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- 400 Bad Request
- Error message about invalid priority

**Verify**:
- [ ] Returns 400 status code
- [ ] Lists valid priority options in error

### 5.3 Invalid Sort Field
```bash
curl "http://localhost:8000/api/1/tasks?sort_by=invalid_field" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- 400 Bad Request
- Error message about invalid sort field

**Verify**:
- [ ] Returns 400 status code
- [ ] Lists valid sort fields in error

### 5.4 Invalid Date Range (Start > End)
```bash
curl "http://localhost:8000/api/1/tasks?due_date_start=2026-02-01T00:00:00&due_date_end=2026-01-01T00:00:00" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected**:
- 400 Bad Request
- Error message about invalid date range

**Verify**:
- [ ] Returns 400 status code
- [ ] Error explains the issue

---

## Test 6: Frontend UI Testing

### Prerequisites
1. Start frontend: `cd frontend && npm run dev`
2. Open browser: http://localhost:3000
3. Sign in to see tasks page

### 6.1 SearchBar Component
- [ ] Type "meeting" in search bar
- [ ] Verify 500ms debounce delay (loading spinner appears)
- [ ] Verify search results appear after delay
- [ ] Verify clear button (X) appears when text is entered
- [ ] Click clear button, verify search clears
- [ ] Press Enter while typing, verify immediate search (no debounce)

### 6.2 FilterPanel Component
- [ ] Open filter panel (on mobile, click "Show Filters" button)
- [ ] Select Status: "Incomplete", verify only incomplete tasks show
- [ ] Select Priority: "High", verify only high-priority tasks show
- [ ] Enter tags: "urgent, work", verify AND logic (both tags required)
- [ ] Select due date range, verify tasks filtered correctly
- [ ] Verify "Clear all" button clears all filters
- [ ] Verify active filter count badge shows correct number

### 6.3 SortControls Component
- [ ] Select Sort By: "Due Date", verify tasks sort by due date
- [ ] Click sort order toggle, verify ascending/descending switch
- [ ] Verify sort direction icon changes (up arrow ↑ / down arrow ↓)
- [ ] Select different sort fields, verify sorting works for each

### 6.4 Search Highlighting (TaskItem)
- [ ] Search for "meeting"
- [ ] Verify "meeting" is highlighted in yellow in task titles
- [ ] Verify "meeting" is highlighted in descriptions
- [ ] Search for "team project"
- [ ] Verify both "team" AND "project" are highlighted

### 6.5 Integration - All Features Together
- [ ] Search for "project"
- [ ] Apply filter: Status = "Incomplete"
- [ ] Apply filter: Priority = "High"
- [ ] Sort by: "Due Date" (ascending)
- [ ] Verify results match all criteria
- [ ] Click "Clear all", verify everything resets

### 6.6 Responsive Design
- [ ] Resize browser to mobile width
- [ ] Verify filter panel is hidden by default on mobile
- [ ] Click "Show Filters" button, verify panel appears
- [ ] Verify all components work on mobile
- [ ] Verify search bar is full-width on mobile

---

## Test Results Summary

Fill out this checklist as you test:

### Backend API Tests
- [ ] Search functionality (Tests 1.1-1.4)
- [ ] Filter functionality (Tests 2.1-2.9)
- [ ] Sort functionality (Tests 3.1-3.5)
- [ ] Pagination (Tests 4.1-4.2)
- [ ] Error handling (Tests 5.1-5.4)

### Frontend UI Tests
- [ ] SearchBar component (Test 6.1)
- [ ] FilterPanel component (Test 6.2)
- [ ] SortControls component (Test 6.3)
- [ ] Search highlighting (Test 6.4)
- [ ] Integration (Test 6.5)
- [ ] Responsive design (Test 6.6)

### Overall Status
- [ ] All backend tests passing
- [ ] All frontend tests passing
- [ ] Phase 6 (User Story 4) complete and ready for production

---

## Common Issues and Solutions

### Issue 1: "401 Unauthorized" errors
**Solution**: Make sure you're using a valid JWT token in the Authorization header

### Issue 2: No search results when expected
**Solution**:
- Verify PostgreSQL GIN index exists on tasks table
- Check that tsvector search is configured correctly
- Try the fallback LIKE search by forcing an error in tsvector

### Issue 3: Filter returns empty results
**Solution**:
- Verify test data exists with the filter criteria
- Check that filter values are exact matches (case-sensitive for some fields)
- Verify tag filter uses AND logic (task must have ALL tags)

### Issue 4: Sort order seems wrong
**Solution**:
- Check that NULL values are handled correctly (e.g., tasks without due_date)
- Verify priority enum order matches expected ranking
- Check that sort_order parameter is "asc" or "desc" (not "ascending"/"descending")

### Issue 5: Frontend debounce not working
**Solution**:
- Check browser console for errors
- Verify debounceDelay prop is set correctly (default 500ms)
- Clear browser cache and restart dev server

---

## Performance Notes

- **Full-text search**: Should handle 10,000+ tasks efficiently with GIN index
- **Filter queries**: Should complete in <100ms for typical datasets
- **Pagination**: Use limit/offset for large result sets
- **Frontend**: Debouncing reduces API calls by ~80% during typing

---

## Next Steps After Testing

1. **If all tests pass**: Mark Phase 6 complete, move to Phase 7
2. **If tests fail**: Document issues, fix bugs, re-test
3. **Performance issues**: Add database indexes, optimize queries
4. **UX improvements**: Gather user feedback, refine UI

---

**Testing Completed By**: ______________
**Date**: ______________
**Result**: ⬜ PASS  ⬜ FAIL (see issues below)

**Issues Found**:
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
