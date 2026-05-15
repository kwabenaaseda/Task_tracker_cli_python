import json
import psycopg2
import os
from datetime import datetime
from src.data.repository import CLEAN, SETUP, formatTime, WRITE, CreateDB
from src.data.db import get_connection

def generateID(list:list):
    
    return len(list) + 1

# SET UP DB

def DB():
    IGNITE = SETUP()
    if (not IGNITE or IGNITE == False):
        print("location0")
        return "Error in DB. Please Retry Action"
    else:
        _database = IGNITE["DB"]
        _tasks = IGNITE["TASKS"]
        return {
            'db':_database,
            "tsc":_tasks
        }

def PostgreSQL():
    from src.data.db import SETUP, format_time, READPS, WRITE
    IGNITE = SETUP()
    if (not IGNITE or IGNITE == False):
        print("location1")
        return "Error in DB. Please Retry Action"
    else:
        _database = IGNITE["DB"]
        _tasks = IGNITE["TASKS"]
        return {
            'db':_database,
            "tsc":_tasks
        }


def Create_task(desc:str, category:str):
    # make sure desc is not empty
    if (desc ==""):
        return json.dumps({
            "status": "error",
            "message": "Please Provide Valid Description for your tasks",
            "body": {}
        })
    
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })

    for el in session["tsc"]:
        if (el["status"]== "TODO" and el['description']==desc.strip()):
            return json.dumps({
                "status": "error",
                "message": "TASK ALREADY EXISTS",
                "body": {}
            })
    
    newTask = {
                "id": generateID(session["tsc"]),
                "description": desc.strip(),
                "category": category.strip(),
                "status": "TODO",
                "created_at": formatTime(),
                "updated_at": formatTime()
            }
    session["tsc"].append(newTask)
    session["db"]["tasks"]= session["tsc"]
    WRITE(session["db"])

    # Write Task to postgres DB
    postgre_session = PostgreSQL()
    if (postgre_session == False or not postgre_session or postgre_session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session with PostgreSQL. Please Try Again.",
            "body": {}
        })
    if (postgre_session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    conn = get_connection()
    if not conn:
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session with PostgreSQL. Please Try Again.",
            "body": {}
        })
    
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (id, description, category, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (newTask["id"], newTask["description"], newTask["category"], newTask["status"], newTask["created_at"], newTask["updated_at"])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting task into PostgreSQL: {e}")
        return json.dumps({
            "status": "error",
            "message": "Error saving task to PostgreSQL. Please Try Again.",
            "body": {}
        })

    response = {
        "status":"success",
        "message":"Task Added",
        "body":{
            "task":newTask["description"],
            "category":newTask["category"],
            "status":newTask["status"],
        }
    }
    return json.dumps(response, separators=(',', ':'))

# List Paths
def List(sort:str):
    accepted = ["all", "todo", "done", "progress"]
    if (sort not in accepted):
        return json.dumps({
            "status": "error",
            "message": "Invalid Sort Option. Accepted options are: all, todo, done, progress",
            "body": {}
        })
    
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    filtered = []
    if (sort == "all"):
        return json.dumps(session["tsc"], separators=(',', ':'))
    elif sort == "todo":
        filtered = [t for t in session["tsc"] if t["status"].upper() == "TODO"]
    elif sort == "done":
        filtered = [t for t in session["tsc"] if t["status"].upper() == "DONE"]
    elif sort == "progress":
        filtered = [t for t in session["tsc"] if t["status"].upper() == "IN_PROGRESS"]
    
    return json.dumps(filtered, separators=(',', ':'))
    

def Status(id:str, status:str):
    if not status.upper() in ["TODO", "IN_PROGRESS", "DONE"]:
        return json.dumps({
            "status": "error",
            "message": "Invalid status. Accepted values are: TODO, IN_PROGRESS, DONE",
            "body": {}
        })
    
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    for el in session["tsc"]:
        if (el["id"]== int(id)):
            el["status"]= status.upper()
            el["updated_at"]= formatTime()
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            
            # Update Task status in postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            if (postgre_session=="Error in DB. Please Retry Action"):
                return json.dumps({
                    "status": "error",
                    "message": "Error in DB. Please Retry Action",
                    "body": {}
                })
            
            conn = get_connection()
            if not conn:
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE tasks SET status = %s, updated_at = %s WHERE id = %s",
                    (el["status"], el["updated_at"], el["id"])
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error updating task in PostgreSQL: {e}")
                return json.dumps({
                    "status": "error",
                    "message": "Error updating task in PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            response = {
                "status":"success",
                "message":"Task Status Updated",
                "body":{
                    "task":el["description"],
                    "category":el["category"],
                    "status":el["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    
    return json.dumps({
        "status": "error",
        "message": "Task Not Found",
        "body": {}
    })

def Update(id:str, desc:str):
    if (desc ==""):
        return json.dumps({
            "status": "error",
            "message": "Please Provide Valid Description for your tasks",
            "body": {}
        })
    
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    for el in session["tsc"]:
        if (el["id"]== int(id)):
            el["description"]= desc.strip()
            el["updated_at"]= formatTime()
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            
            # Update Task description in postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            if (postgre_session=="Error in DB. Please Retry Action"):   
                return json.dumps({
                    "status": "error",
                    "message": "Error in DB. Please Retry Action",
                    "body": {}
                })
            
            conn = get_connection()
            if not conn:
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE tasks SET description = %s, updated_at = %s WHERE id = %s",
                    (el["description"], el["updated_at"], el["id"])
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error updating task in PostgreSQL: {e}")
                return json.dumps({
                    "status": "error",
                    "message": "Error updating task in PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            response = {
                "status":"success",
                "message":"Task Description Updated",
                "body":{
                    "task":el["description"],
                    "category":el["category"],
                    "status":el["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    
    return json.dumps({
        "status": "error",
        "message": "Task Not Found",
        "body": {}
    })

def SetCategory(id:str, category:str):
    """Update the category of a task"""
    if (category == ""):
        return json.dumps({
            "status": "error",
            "message": "Please Provide Valid Category",
            "body": {}
        })
    
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    for el in session["tsc"]:
        if (el["id"]== int(id)):
            el["category"]= category.strip()
            el["updated_at"]= formatTime()
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            
            # Update Task category in postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            if (postgre_session=="Error in DB. Please Retry Action"):   
                return json.dumps({
                    "status": "error",
                    "message": "Error in DB. Please Retry Action",
                    "body": {}
                })
            
            conn = get_connection()
            if not conn:
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE tasks SET category = %s, updated_at = %s WHERE id = %s",
                    (el["category"], el["updated_at"], el["id"])
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error updating task category in PostgreSQL: {e}")
                return json.dumps({
                    "status": "error",
                    "message": "Error updating task in PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            response = {
                "status":"success",
                "message":"Task Category Updated",
                "body":{
                    "task":el["description"],
                    "category":el["category"],
                    "status":el["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    
    return json.dumps({
        "status": "error",
        "message": "Task Not Found",
        "body": {}
    })

def Delete(id:str):
    session = DB()
    if (session == False or not session or session == None):
        return json.dumps({
            "status": "error",
            "message": "Could not establish user session. Please Try Again.",
            "body": {}
        })
    
    if (session=="Error in DB. Please Retry Action"):
        return json.dumps({
            "status": "error",
            "message": "Error in DB. Please Retry Action",
            "body": {}
        })
    
    for i, el in enumerate(session["tsc"]):
        if (el["id"]== int(id)):
            deleted_task = session["tsc"].pop(i)
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            
            # Delete Task from postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            if (postgre_session=="Error in DB. Please Retry Action"):
                return json.dumps({
                    "status": "error",
                    "message": "Error in DB. Please Retry Action",
                    "body": {}
                })
            
            conn = get_connection()
            if not conn:
                return json.dumps({
                    "status": "error",
                    "message": "Could not establish user session with PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM tasks WHERE id = %s",
                    (el["id"],)
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error deleting task from PostgreSQL: {e}")
                return json.dumps({
                    "status": "error",
                    "message": "Error deleting task from PostgreSQL. Please Try Again.",
                    "body": {}
                })
            
            response = {
                "status":"success",
                "message":"Task Deleted",
                "body":{
                    "task":deleted_task["description"],
                    "category":deleted_task["category"],
                    "status":deleted_task["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    
    return json.dumps({
        "status": "error",
        "message": "Task Not Found",
        "body": {}
    })

def Help():
    return """
    Available Commands:
    - add <description> [:<category>]: Create a new task with description and optional category.
      Example: add Buy groceries:Shopping
      Example: add Learn Docker (defaults to General)
    
    - list [--todo|--done|--progress]: List tasks, optionally filtered by status.
    
    - category <id> <category_name>: Update task category.
      Example: category 1 Work
    
    - status <id> <status>: Update task status (TODO, IN_PROGRESS, DONE).
    
    - update <id> <description>: Update task description.
    
    - delete <id>: Delete a task by its ID.
    
    - help: Show this help message.
    
    - clean: Delete all tasks.
    
    - exit: Exit the application.
    """

def CleanHouse():
    CLEAN()
    response = {
        "status":"success",
        "message":"All Tasks Cleared",
    }
    return json.dumps(response, separators=(',', ':'))


__all__ = ["Create_task", "List", "Status", "Update", "Delete", "SetCategory", "Help", "CleanHouse"]