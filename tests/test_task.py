import sys
import os
import pytest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logic.task import Create_task
from src.data import repository

@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    test_file = str(tmp_path / "tasks.json")
    repository.TASKS_FILE = test_file
    yield test_file

def test_create_task(test_db):
    """Test: Creating a new task should succeed"""
    result = Create_task("Buy groceries")
    
    # Parse JSON response
    data = json.loads(result)
    
    assert data["status"] == "success", f"Expected status success, got {data['status']}"
    assert data["message"] == "Task Added"
    assert data["body"]["task"] == "Buy groceries"
    print("✓ Test 1 passed: Valid task created")

def test_empty_description(test_db):
    """Test: Empty description should be rejected"""
    result = Create_task("")
    
    # This returns a plain string error, not JSON
    assert "Please Provide" in result
    print("✓ Test 2 passed: Empty description rejected")

def test_duplicate_task(test_db):
    """Test: Duplicate task should be rejected"""
    result1 = Create_task("Buy groceries")
    result2 = Create_task("Buy groceries")
    
    # First should succeed (JSON)
    data1 = json.loads(result1)
    assert data1["status"] == "success"
    
    # Second should fail (plain string)
    assert "TASK ALREADY EXISTS" in result2
    print("✓ Test 3 passed: Duplicate task rejected")

def test_task_persistence(test_db):
    """Test: Created task should be readable from file"""
    Create_task("Learn Rust")
    
    # Read the file directly
    with open(test_db, 'r') as f:
        data = json.load(f)
    
    # Find the task we just created
    learn_rust_tasks = [t for t in data["tasks"] if t["description"] == "Learn Rust"]
    
    assert len(learn_rust_tasks) == 1, f"Expected 1 'Learn Rust' task, got {len(learn_rust_tasks)}"
    assert learn_rust_tasks[0]["status"] == "TODO"
    print("✓ Test 4 passed: Task persisted to file")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])