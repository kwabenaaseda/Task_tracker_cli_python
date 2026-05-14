import json
import os
from datetime import datetime
from src.data.db import READPS, WRITE

# Make this configurable for testing
TASKS_FILE = os.getenv("TASKS_FILE", "tasks.json")

def formatTime():
    return datetime.utcnow().isoformat() + "Z"

DEFAULT = {
    "title": "TASK MANAGER",
    "owner": "kwabenaaseda",
    "created_at": formatTime(),
    "updated_at": formatTime(),
    "tasks": [
        {
            "id": 0,
            "description": "Welcome to Task Manager 1.0. Happy Productivity",
            "status": "TODO",
            "created_at": formatTime(),
            "updated_at": formatTime()
        }
    ]
}

def CreateDB():
    # First Read Postgres DB for data and import that to json file. This is a one time operation. After that, we will only interact with the json file. If it fails , use dafault data to create json file. This is a fallback mechanism to ensure the app is always functional, even if the database connection fails.
    db_data = READPS()
    if db_data and db_data != False:
            try:
                with open(TASKS_FILE, mode="w", encoding="utf-8") as f:
                    json.dump(db_data, f, separators=(',', ":"))
                return True
            except IOError as e:
                print(f"Error writing DB: {e}")
                return False
    
        # If we couldn't read from the database, create a new file with default data

    """Create a new tasks.json file with default data"""
    with open(TASKS_FILE, mode="w", encoding="utf-8") as f:
        json.dump(DEFAULT, f, separators=(',', ":"))
    return True


def CLEAN():
    # Remove all entries from the database and then update the json file to reflect that change. This ensures both data sources are in sync.
    # First, we would need to implement a function in db.py to clear all tasks from the database. For now, let's assume we have a function called CLEARDB() that does this.
    from src.data.db import CLEARDB
    db_clear_result = CLEARDB()
    if not db_clear_result:
        print("Error clearing database. Please try again.")
        return False
    # Now, we need to update the json file to reflect the cleared database. We can do this by writing an empty tasks list to the file.
    empty_db = {
        "title": "TASK MANAGER",
        "owner": "kwabenaaseda",
        "created_at": formatTime(),
        "updated_at": formatTime(),
        "tasks": []
    }
    with open(TASKS_FILE, mode="w", encoding="utf-8") as f:
        json.dump(empty_db, f, separators=(',', ":"))
    return True

def read_call():
    """Read tasks from file. Create if doesn't exist."""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, mode="r", encoding="utf-8") as f:
                raw = f.read()
                result = json.loads(raw)
                return result
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading DB: {e}")
            return None
    else:
        # File doesn't exist, create it
        CreateDB()
        # Now read it back
        with open(TASKS_FILE, mode="r", encoding="utf-8") as f:
            result = json.loads(f.read())
            return result

def write_call(payload: dict):
    """Write tasks to file"""
    try:
        with open(TASKS_FILE, mode="w", encoding="utf-8") as f:
            json.dump(payload, f, separators=(',', ":"))
        return True
    except IOError as e:
        print(f"Error writing DB: {e}")
        return False

def READ():
    """Wrapper for read_call - returns dict or False"""
    db = read_call()
    if not db:
        return False
    return db

def WRITE(payload: dict):
    """Wrapper for write_call - returns True or False"""
    result = write_call(payload)
    return True if result else False

def SETUP():
    """Set up database and return dict with DB and TASKS"""
    call = READ()
    if not call or call == False:
        return False
    
    DATABASE = call
    
    TASKS = DATABASE["tasks"]
    if type(TASKS) != list:
        return False
    
    return {
        "DB": DATABASE,
        "TASKS": TASKS
    }

__all__ = ["READ", "WRITE", "SETUP", "formatTime", "TASKS_FILE", "CLEAN"]