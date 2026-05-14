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


def Create_task(desc:str):
    # make sure desc is not empty
    if (desc ==""):
        return "Please Provide Valid Description for your tasks"
    
    session = DB()
    if (session == False or not session or session == None):
        return "Could not establish user session. Please Try Again."
    
    if (session=="Error in DB. Please Retry Action"):
        
        return session

    for el in session["tsc"]:
        if (el["status"]== "TODO" and el['description']==desc.strip()):
            
            return "TASK ALREADY EXISTS"
    
    newTask = {
                "id": generateID(session["tsc"]),
                "description": desc.strip(),
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
        return "Could not establish user session with PostgreSQL. Please Try Again."
    if (postgre_session=="Error in DB. Please Retry Action"):
        return postgre_session
    # Here we would have a function like `INSERT_TASK(newTask)` that handles the actual insertion into the PostgreSQL database. This is a placeholder to indicate where that logic would go.
    conn = get_connection()
    if not conn:
        return "Could not establish user session with PostgreSQL. Please Try Again."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (id, description, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (newTask["id"], newTask["description"], newTask["status"], newTask["created_at"], newTask["updated_at"])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting task into PostgreSQL: {e}")
        return "Error saving task to PostgreSQL. Please Try Again."


    response = {
        "status":"success",
        "message":"Task Added",
        "body":{
            "task":newTask["description"],
            "status":newTask["status"],
        }
    }
    return json.dumps(response, separators=(',', ':'))

# List Paths
def List(sort:str):
    accepted = ["all", "todo", "done", "progress"]
    if (sort not in accepted):
        return "Invalid Sort Option. Accepted options are: all, todo, done, progress"
    session = DB()
    if (session == False or not session or session == None):
        return "Could not establish user session. Please Try Again."
    if (session=="Error in DB. Please Retry Action"):
        return session
    if (sort == "all"):
        return json.dumps(session["tsc"], separators=(',', ':'))
    else:
        filtered = [t for t in session["tsc"] if t["status"].lower() == sort]
        return json.dumps(filtered, separators=(',', ':'))
    

def Status(id:str, status:str):
    if not status.upper() in ["TODO", "IN_PROGRESS", "DONE"]:
        return "Invalid status. Accepted values are: TODO, IN_PROGRESS, DONE"
    session = DB()
    if (session == False or not session or session == None):
        return "Could not establish user session. Please Try Again."
    if (session=="Error in DB. Please Retry Action"):
        return session
    for el in session["tsc"]:
        if (el["id"]== int(id)):
            el["status"]= status.upper()
            el["updated_at"]= formatTime()
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            # Update Task status in postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return "Could not establish user session with PostgreSQL. Please Try Again."
            if (postgre_session=="Error in DB. Please Retry Action"):
                return postgre_session
            conn = get_connection()
            if not conn:
                return "Could not establish user session with PostgreSQL. Please Try Again."
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
                return "Error updating task in PostgreSQL. Please Try Again."
            
            response = {
                "status":"success",
                "message":"Task Status Updated",
                "body":{
                    "task":el["description"],
                    "status":el["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    return "Task Not Found"

def Update(id:str, desc:str):
    if (desc ==""):
        return "Please Provide Valid Description for your tasks"
    session = DB()
    if (session == False or not session or session == None):
        return "Could not establish user session. Please Try Again."
    if (session=="Error in DB. Please Retry Action"):
        return session
    for el in session["tsc"]:
        if (el["id"]== int(id)):
            el["description"]= desc.strip()
            el["updated_at"]= formatTime()
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            # Update Task description in postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return "Could not establish user session with PostgreSQL. Please Try Again."
            if (postgre_session=="Error in DB. Please Retry Action"):   
                return postgre_session
            conn = get_connection()
            if not conn:
                return "Could not establish user session with PostgreSQL. Please Try Again."
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
                return "Error updating task in PostgreSQL. Please Try Again."
            response = {
                "status":"success",
                "message":"Task Description Updated",
                "body":{
                    "task":el["description"],
                    "status":el["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    return "Task Not Found"

def Delete(id:str):
    session = DB()
    if (session == False or not session or session == None):
        return "Could not establish user session. Please Try Again."
    if (session=="Error in DB. Please Retry Action"):
        return session
    for i, el in enumerate(session["tsc"]):
        if (el["id"]== int(id)):
            deleted_task = session["tsc"].pop(i)
            session["db"]["tasks"]= session["tsc"]
            WRITE(session["db"])
            # Delete Task from postgres DB
            postgre_session = PostgreSQL()
            if (postgre_session == False or not postgre_session or postgre_session == None):
                return "Could not establish user session with PostgreSQL. Please Try Again."
            if (postgre_session=="Error in DB. Please Retry Action"):
                return postgre_session
            conn = get_connection()
            if not conn:
                return "Could not establish user session with PostgreSQL. Please Try Again."
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
                return "Error deleting task from PostgreSQL. Please Try Again."
            response = {
                "status":"success",
                "message":"Task Deleted",
                "body":{
                    "task":deleted_task["description"],
                    "status":deleted_task["status"],
                }
            }
            return json.dumps(response, separators=(',', ':'))
    return "Task Not Found"

def Help():
    return """
    Available Commands:
    - add <description>: Create a new task with the given description.
    - list [--todo|--done|--progress]: List tasks, optionally filtered by status.
    - status <id> <status>: Update the status of a task (TODO, IN_PROGRESS, DONE).
    - update <id> <description>: Update the description of a task.
    - delete <id>: Delete a task by its ID.
    - help: Show this help message.
    - exit: Exit the application.
    """

def CleanHouse():
    CLEAN()
    response = {
        "status":"success",
        "message":"All Tasks Cleared",
    }
    return json.dumps(response, separators=(',', ':'))


__all__ = ["Create_task", "List", "Status", "Update", "Delete", "Help", "CleanHouse"]