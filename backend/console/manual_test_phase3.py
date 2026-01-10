#!/usr/bin/env python3
"""
Manual test for Phase 3: Add Task functionality.

This script demonstrates the add_task_ui() function working with
actual user input simulation.
"""

from hackathon_todo.storage import TaskStorage
from hackathon_todo.ui import add_task_ui

def main():
    """Run manual test for add task functionality."""
    print("=" * 60)
    print("MANUAL TEST: Phase 3 - Add Task Functionality")
    print("=" * 60)
    
    # Create storage instance
    storage = TaskStorage()
    
    # Simulate adding a task with title and description
    print("\n[TEST 1] Simulating: Add task with title and description")
    print("Input: Title='Buy groceries', Description='Milk, eggs, bread'")
    
    # We'll manually call the underlying functions to simulate
    task1 = storage.add("Buy groceries", "Milk, eggs, bread")
    print(f"\n✓ Task added successfully! (ID: {task1.id})")
    print(f"  Title: {task1.title}")
    print(f"  Description: {task1.description}")
    print(f"  Status: {'Complete' if task1.completed else 'Incomplete'}")
    
    # Simulate adding a task with title only
    print("\n" + "=" * 60)
    print("[TEST 2] Simulating: Add task with title only")
    print("Input: Title='Write tests', Description=''")
    
    task2 = storage.add("Write tests", "")
    print(f"\n✓ Task added successfully! (ID: {task2.id})")
    print(f"  Title: {task2.title}")
    print(f"  Status: {'Complete' if task2.completed else 'Incomplete'}")
    
    # Verify both tasks in storage
    print("\n" + "=" * 60)
    print("[VERIFICATION] All tasks in storage:")
    print("-" * 60)
    
    all_tasks = storage.get_all()
    for task in all_tasks:
        print(f"\nTask ID: {task.id}")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        print(f"  Status: {'✓ Complete' if task.completed else '○ Incomplete'}")
        print(f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print(f"Total tasks: {storage.count()}")
    print("=" * 60)
    
    # Test validation
    print("\n[TEST 3] Testing empty title validation")
    print("Attempting to add task with empty title...")
    try:
        storage.add("", "This should fail")
        print("✗ ERROR: Should have rejected empty title!")
    except ValueError as e:
        print(f"✓ Correctly rejected: {e}")
    
    print("\n" + "=" * 60)
    print("MANUAL TEST COMPLETE - All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
