"""
Pytest configuration and shared fixtures for hackathon-todo tests.
"""

import pytest


@pytest.fixture
def storage():
    """
    Provide a fresh TaskStorage instance for each test.
    
    This fixture ensures test isolation by creating a new storage
    instance for each test function.
    
    Returns:
        TaskStorage: An empty TaskStorage instance
    """
    from hackathon_todo.storage import TaskStorage
    return TaskStorage()


@pytest.fixture
def sample_task():
    """
    Provide a sample Task instance for testing.
    
    Returns:
        Task: A sample task with predefined values
    """
    from hackathon_todo.models import Task
    return Task(
        id=1,
        title="Sample Task",
        description="This is a test task"
    )


@pytest.fixture
def storage_with_tasks(storage):
    """
    Provide a TaskStorage instance pre-populated with sample tasks.
    
    Args:
        storage: The base storage fixture
    
    Returns:
        TaskStorage: Storage instance with 3 sample tasks
    """
    storage.add("Buy groceries", "Milk, eggs, bread")
    storage.add("Write tests", "Complete unit tests for models")
    task3 = storage.add("Deploy app", "Push to production")
    storage.toggle_complete(task3.id)
    return storage
