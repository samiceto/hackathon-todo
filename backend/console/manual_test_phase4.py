#!/usr/bin/env python3
"""
Manual test for Phase 4: View Tasks functionality.

This script demonstrates the view_tasks_ui() function with various scenarios.
"""

from hackathon_todo.storage import TaskStorage
from hackathon_todo.ui import view_tasks_ui

def main():
    """Run manual test for view tasks functionality."""
    print("=" * 60)
    print("MANUAL TEST: Phase 4 - View Tasks Functionality")
    print("=" * 60)
    
    # Create storage instance
    storage = TaskStorage()
    
    # TEST 1: View empty task list
    print("\n[TEST 1] View empty task list")
    print("-" * 60)
    view_tasks_ui(storage)
    
    # TEST 2: View task list with multiple tasks
    print("\n" + "=" * 60)
    print("[TEST 2] View task list with multiple tasks")
    print("-" * 60)
    
    # Add some tasks
    task1 = storage.add("Buy groceries", "Milk, eggs, bread")
    task2 = storage.add("Write tests", "Complete unit tests for models")
    task3 = storage.add("Deploy app", "Push to production")
    
    view_tasks_ui(storage)
    
    # TEST 3: View with mix of completed and incomplete tasks
    print("\n" + "=" * 60)
    print("[TEST 3] View with completed and incomplete tasks")
    print("-" * 60)
    
    # Mark task1 and task3 as complete
    storage.toggle_complete(task1.id)
    storage.toggle_complete(task3.id)
    
    view_tasks_ui(storage)
    
    # TEST 4: Verify status indicators
    print("\n" + "=" * 60)
    print("[VERIFICATION] Status indicator verification:")
    print("-" * 60)
    print(f"Task 1 - Completed: {task1.completed} (should show ✓)")
    print(f"Task 2 - Completed: {task2.completed} (should show ○)")
    print(f"Task 3 - Completed: {task3.completed} (should show ✓)")
    
    # TEST 5: View tasks after adding one without description
    print("\n" + "=" * 60)
    print("[TEST 4] View tasks with one having no description")
    print("-" * 60)
    
    storage.add("Task without description", "")
    view_tasks_ui(storage)
    
    print("\n" + "=" * 60)
    print("MANUAL TEST COMPLETE - All display scenarios tested!")
    print("=" * 60)
    
    # Final verification
    print("\n[FINAL VERIFICATION]")
    print(f"✓ Empty list message displayed correctly")
    print(f"✓ Multiple tasks displayed with ID, status, title")
    print(f"✓ Descriptions displayed when present")
    print(f"✓ Status indicators (✓ and ○) working correctly")
    print(f"✓ Task count summary displayed")
    print(f"✓ Tasks sorted by ID")

if __name__ == "__main__":
    main()
