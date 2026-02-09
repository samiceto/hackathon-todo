#!/usr/bin/env python3
"""
Test script for backend CRUD operations on Kubernetes deployment
Task T033: Test backend CRUD operations through API

This script generates a JWT token and tests all task endpoints:
- Create task
- List tasks
- Get single task
- Update task
- Toggle completion
- Delete task

Usage:
    python test_backend_crud.py [--host localhost] [--port 8000]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

import requests
from jose import jwt

# Configuration (override with command-line args)
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
DEFAULT_USER_ID = 1
DEFAULT_EMAIL = "test@example.com"


def generate_test_jwt(
    user_id: int,
    email: str,
    secret: str,
    algorithm: str = "HS256",
    expires_minutes: int = 30
) -> str:
    """Generate a test JWT token for authentication.

    Args:
        user_id: User ID for the token
        email: Email for the token
        secret: JWT secret key (BETTER_AUTH_SECRET)
        algorithm: JWT algorithm (default: HS256)
        expires_minutes: Token expiration time in minutes

    Returns:
        Encoded JWT token string
    """
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

    payload = {
        "sub": str(user_id),  # User ID as subject
        "email": email,
        "exp": expires_at,
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token


def test_backend_crud(
    base_url: str,
    token: str,
    user_id: int
) -> bool:
    """Test all backend CRUD operations.

    Args:
        base_url: Backend API base URL (e.g., http://localhost:8000)
        token: JWT token for authentication
        user_id: User ID for API calls

    Returns:
        True if all tests pass, False otherwise
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n{'='*60}")
    print(f"Testing Backend CRUD Operations")
    print(f"Base URL: {base_url}")
    print(f"User ID: {user_id}")
    print(f"{'='*60}\n")

    created_task_id = None

    try:
        # Test 1: Create Task
        print("✓ Test 1: Create Task")
        create_response = requests.post(
            f"{base_url}/api/{user_id}/tasks",
            headers=headers,
            json={
                "title": "Test Task from K8s Deployment",
                "description": "Testing CRUD operations on Kubernetes backend"
            }
        )

        if create_response.status_code != 201:
            print(f"  ✗ FAILED: Expected 201, got {create_response.status_code}")
            print(f"  Response: {create_response.text}")
            return False

        created_task = create_response.json()
        created_task_id = created_task["id"]
        print(f"  ✓ SUCCESS: Created task ID {created_task_id}")
        print(f"  Title: {created_task['title']}")
        print(f"  Completed: {created_task['completed']}")

        # Test 2: List Tasks
        print("\n✓ Test 2: List Tasks")
        list_response = requests.get(
            f"{base_url}/api/{user_id}/tasks",
            headers=headers
        )

        if list_response.status_code != 200:
            print(f"  ✗ FAILED: Expected 200, got {list_response.status_code}")
            return False

        tasks_data = list_response.json()
        print(f"  ✓ SUCCESS: Retrieved {tasks_data['total']} tasks")

        # Test 3: Get Single Task
        print("\n✓ Test 3: Get Single Task")
        get_response = requests.get(
            f"{base_url}/api/{user_id}/tasks/{created_task_id}",
            headers=headers
        )

        if get_response.status_code != 200:
            print(f"  ✗ FAILED: Expected 200, got {get_response.status_code}")
            return False

        task = get_response.json()
        print(f"  ✓ SUCCESS: Retrieved task ID {task['id']}")
        print(f"  Title: {task['title']}")

        # Test 4: Update Task
        print("\n✓ Test 4: Update Task")
        update_response = requests.put(
            f"{base_url}/api/{user_id}/tasks/{created_task_id}",
            headers=headers,
            json={
                "title": "Updated Test Task",
                "description": "Updated description for K8s testing"
            }
        )

        if update_response.status_code != 200:
            print(f"  ✗ FAILED: Expected 200, got {update_response.status_code}")
            return False

        updated_task = update_response.json()
        print(f"  ✓ SUCCESS: Updated task ID {updated_task['id']}")
        print(f"  New title: {updated_task['title']}")

        # Test 5: Toggle Completion
        print("\n✓ Test 5: Toggle Task Completion")
        toggle_response = requests.patch(
            f"{base_url}/api/{user_id}/tasks/{created_task_id}/complete",
            headers=headers
        )

        if toggle_response.status_code != 200:
            print(f"  ✗ FAILED: Expected 200, got {toggle_response.status_code}")
            return False

        toggled_task = toggle_response.json()
        print(f"  ✓ SUCCESS: Toggled completion status")
        print(f"  Completed: {toggled_task['completed']}")

        # Test 6: Delete Task
        print("\n✓ Test 6: Delete Task")
        delete_response = requests.delete(
            f"{base_url}/api/{user_id}/tasks/{created_task_id}",
            headers=headers
        )

        if delete_response.status_code != 204:
            print(f"  ✗ FAILED: Expected 204, got {delete_response.status_code}")
            return False

        print(f"  ✓ SUCCESS: Deleted task ID {created_task_id}")

        # Verify deletion
        verify_response = requests.get(
            f"{base_url}/api/{user_id}/tasks/{created_task_id}",
            headers=headers
        )

        if verify_response.status_code != 404:
            print(f"  ✗ FAILED: Task still exists after deletion")
            return False

        print(f"  ✓ VERIFIED: Task no longer exists (404)")

        print(f"\n{'='*60}")
        print("✓ ALL TESTS PASSED!")
        print(f"{'='*60}\n")

        return True

    except requests.exceptions.ConnectionError:
        print(f"\n✗ CONNECTION FAILED: Could not connect to {base_url}")
        print("  Make sure the backend is deployed and accessible via port-forward:")
        print(f"  kubectl port-forward svc/todo-app-backend {DEFAULT_PORT}:8000")
        return False

    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return False


def main():
    """Main function to run CRUD tests."""
    parser = argparse.ArgumentParser(
        description="Test backend CRUD operations on Kubernetes deployment"
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Backend host (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Backend port (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=DEFAULT_USER_ID,
        help=f"User ID for testing (default: {DEFAULT_USER_ID})"
    )
    parser.add_argument(
        "--email",
        default=DEFAULT_EMAIL,
        help=f"Email for JWT token (default: {DEFAULT_EMAIL})"
    )
    parser.add_argument(
        "--secret",
        help="BETTER_AUTH_SECRET for JWT token (required)"
    )

    args = parser.parse_args()

    # Validate secret
    if not args.secret:
        print("ERROR: --secret argument is required")
        print("\nGet the secret from your deployment:")
        print("  kubectl get secret todo-app-backend-secrets -o jsonpath='{.data.BETTER_AUTH_SECRET}' | base64 -d")
        sys.exit(1)

    # Build base URL
    base_url = f"http://{args.host}:{args.port}"

    # Generate JWT token
    print("Generating test JWT token...")
    token = generate_test_jwt(
        user_id=args.user_id,
        email=args.email,
        secret=args.secret
    )
    print(f"Token: {token[:50]}...")

    # Run tests
    success = test_backend_crud(base_url, token, args.user_id)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
