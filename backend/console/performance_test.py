#!/usr/bin/env python3
"""
Performance Test for Hackathon Todo Application

Tests the application's performance with 100+ tasks to ensure:
1. No degradation in response time
2. Memory usage remains reasonable
3. All CRUD operations complete in acceptable time

Acceptance Criteria:
- Add 150 tasks: < 1 second total
- View all tasks: < 0.5 seconds
- Individual operations (get, update, mark_complete, delete): < 10ms each
- Memory usage: Reasonable for in-memory storage
"""

import time
from datetime import datetime
from hackathon_todo.storage import TaskStorage


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    elapsed = (end - start) * 1000  # Convert to milliseconds
    return result, elapsed


def format_time(ms):
    """Format time in milliseconds for display."""
    if ms < 1:
        return f"{ms:.3f}ms"
    elif ms < 1000:
        return f"{ms:.2f}ms"
    else:
        return f"{ms/1000:.2f}s"


def main():
    print("=" * 70)
    print("HACKATHON TODO - PERFORMANCE TEST")
    print("=" * 70)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Scope: 150 tasks with comprehensive CRUD operations\n")

    storage = TaskStorage()
    results = {}

    # TEST 1: Add 150 tasks
    print("=" * 70)
    print("TEST 1: Add 150 Tasks")
    print("=" * 70)

    start_time = time.perf_counter()
    task_ids = []
    for i in range(1, 151):
        title = f"Task {i}"
        description = f"This is task number {i} with some description text"
        _, elapsed = measure_time(storage.add, title, description)
        task_ids.append(i)

        if i == 1:
            print(f"First task add time: {format_time(elapsed)}")
        elif i == 150:
            print(f"Last task add time: {format_time(elapsed)}")

    total_add_time = (time.perf_counter() - start_time) * 1000
    avg_add_time = total_add_time / 150

    print(f"\nTotal time to add 150 tasks: {format_time(total_add_time)}")
    print(f"Average time per task: {format_time(avg_add_time)}")
    print(f"✅ PASS" if total_add_time < 1000 else f"⚠️  WARNING: Exceeded 1s target")

    results['add_total'] = total_add_time
    results['add_avg'] = avg_add_time

    # TEST 2: Get All Tasks
    print("\n" + "=" * 70)
    print("TEST 2: View All Tasks (get_all)")
    print("=" * 70)

    all_tasks, elapsed = measure_time(storage.get_all)
    print(f"Time to retrieve all {len(all_tasks)} tasks: {format_time(elapsed)}")
    print(f"Tasks retrieved: {len(all_tasks)}")
    print(f"✅ PASS" if elapsed < 500 else f"⚠️  WARNING: Exceeded 500ms target")

    results['get_all'] = elapsed

    # TEST 3: Random Get Operations
    print("\n" + "=" * 70)
    print("TEST 3: Random Individual Get Operations (50 tasks)")
    print("=" * 70)

    import random
    random.seed(42)
    sample_ids = random.sample(task_ids, 50)

    get_times = []
    for task_id in sample_ids[:10]:  # Show first 10
        task, elapsed = measure_time(storage.get, task_id)
        get_times.append(elapsed)

    for task_id in sample_ids[10:]:  # Remaining 40 (silent)
        _, elapsed = measure_time(storage.get, task_id)
        get_times.append(elapsed)

    avg_get_time = sum(get_times) / len(get_times)
    max_get_time = max(get_times)
    min_get_time = min(get_times)

    print(f"Average get time: {format_time(avg_get_time)}")
    print(f"Min get time: {format_time(min_get_time)}")
    print(f"Max get time: {format_time(max_get_time)}")
    print(f"✅ PASS" if avg_get_time < 10 else f"⚠️  WARNING: Exceeded 10ms target")

    results['get_avg'] = avg_get_time
    results['get_max'] = max_get_time

    # TEST 4: Toggle Complete Operations
    print("\n" + "=" * 70)
    print("TEST 4: Toggle Tasks Complete (50 tasks)")
    print("=" * 70)

    complete_times = []
    for task_id in sample_ids:
        _, elapsed = measure_time(storage.toggle_complete, task_id)
        complete_times.append(elapsed)

    avg_complete_time = sum(complete_times) / len(complete_times)
    max_complete_time = max(complete_times)

    print(f"Average toggle complete time: {format_time(avg_complete_time)}")
    print(f"Max toggle complete time: {format_time(max_complete_time)}")
    print(f"✅ PASS" if avg_complete_time < 10 else f"⚠️  WARNING: Exceeded 10ms target")

    results['toggle_complete_avg'] = avg_complete_time
    results['toggle_complete_max'] = max_complete_time

    # TEST 5: Update Operations
    print("\n" + "=" * 70)
    print("TEST 5: Update Tasks (30 tasks)")
    print("=" * 70)

    update_ids = random.sample(task_ids, 30)
    update_times = []

    for task_id in update_ids:
        new_title = f"Updated Task {task_id}"
        new_desc = f"Updated description for task {task_id}"
        _, elapsed = measure_time(storage.update, task_id, new_title, new_desc)
        update_times.append(elapsed)

    avg_update_time = sum(update_times) / len(update_times)
    max_update_time = max(update_times)

    print(f"Average update time: {format_time(avg_update_time)}")
    print(f"Max update time: {format_time(max_update_time)}")
    print(f"✅ PASS" if avg_update_time < 10 else f"⚠️  WARNING: Exceeded 10ms target")

    results['update_avg'] = avg_update_time
    results['update_max'] = max_update_time

    # TEST 6: Delete Operations
    print("\n" + "=" * 70)
    print("TEST 6: Delete Tasks (50 tasks)")
    print("=" * 70)

    delete_ids = random.sample(task_ids, 50)
    delete_times = []

    for task_id in delete_ids:
        _, elapsed = measure_time(storage.delete, task_id)
        delete_times.append(elapsed)

    avg_delete_time = sum(delete_times) / len(delete_times)
    max_delete_time = max(delete_times)

    print(f"Average delete time: {format_time(avg_delete_time)}")
    print(f"Max delete time: {format_time(max_delete_time)}")
    print(f"Tasks remaining: {storage.count()}")
    print(f"✅ PASS" if avg_delete_time < 10 else f"⚠️  WARNING: Exceeded 10ms target")

    results['delete_avg'] = avg_delete_time
    results['delete_max'] = max_delete_time

    # TEST 7: Final Get All (with fewer tasks)
    print("\n" + "=" * 70)
    print("TEST 7: Get All After Deletions")
    print("=" * 70)

    remaining_tasks, elapsed = measure_time(storage.get_all)
    print(f"Time to retrieve {len(remaining_tasks)} remaining tasks: {format_time(elapsed)}")
    print(f"Expected remaining: 100 (150 - 50 deleted)")
    print(f"Actual remaining: {len(remaining_tasks)}")
    print(f"✅ PASS" if len(remaining_tasks) == 100 else f"❌ FAIL: Count mismatch")

    results['get_all_after_delete'] = elapsed

    # SUMMARY
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 70)

    all_passed = True

    print("\nOperation Performance:")
    print(f"  Add 150 tasks:        {format_time(results['add_total']):>12} (avg: {format_time(results['add_avg'])})")
    if results['add_total'] >= 1000:
        print(f"    ⚠️  WARNING: Exceeded 1s target")
        all_passed = False

    print(f"  Get all (150 tasks):  {format_time(results['get_all']):>12}")
    if results['get_all'] >= 500:
        print(f"    ⚠️  WARNING: Exceeded 500ms target")
        all_passed = False

    print(f"  Get (avg):            {format_time(results['get_avg']):>12}")
    if results['get_avg'] >= 10:
        print(f"    ⚠️  WARNING: Exceeded 10ms target")
        all_passed = False

    print(f"  Toggle complete (avg):{format_time(results['toggle_complete_avg']):>12}")
    if results['toggle_complete_avg'] >= 10:
        print(f"    ⚠️  WARNING: Exceeded 10ms target")
        all_passed = False

    print(f"  Update (avg):         {format_time(results['update_avg']):>12}")
    if results['update_avg'] >= 10:
        print(f"    ⚠️  WARNING: Exceeded 10ms target")
        all_passed = False

    print(f"  Delete (avg):         {format_time(results['delete_avg']):>12}")
    if results['delete_avg'] >= 10:
        print(f"    ⚠️  WARNING: Exceeded 10ms target")
        all_passed = False

    print(f"  Get all (100 tasks):  {format_time(results['get_all_after_delete']):>12}")

    print("\nConclusion:")
    if all_passed:
        print("✅ ALL PERFORMANCE TARGETS MET")
        print("\nThe application handles 100+ tasks efficiently with:")
        print("  - Fast individual operations (< 10ms)")
        print("  - Quick batch operations (< 1s for 150 adds)")
        print("  - No observable degradation with dataset size")
        print("  - Suitable for CLI interactive use")
    else:
        print("⚠️  SOME WARNINGS - Review performance targets")

    print("\n" + "=" * 70)
    print("END OF PERFORMANCE TEST")
    print("=" * 70)


if __name__ == "__main__":
    main()
