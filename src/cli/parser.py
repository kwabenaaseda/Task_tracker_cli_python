import json
from src.logic.task import Create_task, List, Status, Update, Delete, Help, CleanHouse, SetCategory

def router(inp: str):
    """Route user commands to appropriate handlers"""
    x = inp.split(" ")
    
    if len(x) == 0 or not x[0]:
        return None
    
    command = x[0].lower()
    args = x[1:] if len(x) > 1 else []
    
    # ===== ADD TASK =====
    if command == "add":
        if not args:
            return json.dumps({
                "status": "error",
                "message": "Please provide task description",
                "body": {}
            })
        
        # Parse: add <description> or add <description> [category]
        # If last arg looks like a category (no spaces), treat it as category
        # Otherwise treat entire input as description
        
        description = " ".join(args)
        category = "General"  # default
        
        # Simple heuristic: if description contains a colon, treat as "description:category"
        if ":" in description:
            parts = description.rsplit(":", 1)  # split from right (last colon)
            description = parts[0].strip()
            category = parts[1].strip() if parts[1].strip() else "General"
        
        return Create_task(description, category)
    
    # ===== LIST TASKS =====
    elif command == "list":
        if not args:
            return List("all")
        elif args[0] == "--todo":
            return List("todo")
        elif args[0] == "--done":
            return List("done")
        elif args[0] == "--progress":
            return List("progress")
        else:
            return List("all")
    
    # ===== SET CATEGORY =====
    elif command == "category":
        if len(args) < 2:
            return json.dumps({
                "status": "error",
                "message": "Usage: category <id> <category_name>",
                "body": {}
            })
        task_id = args[0]
        category = " ".join(args[1:])
        return SetCategory(task_id, category)
    
    # ===== CHANGE STATUS =====
    elif command == "status":
        if len(args) < 2:
            return json.dumps({
                "status": "error",
                "message": "Usage: status <id> <status>",
                "body": {}
            })
        task_id = args[0]
        status = args[1]
        return Status(task_id, status)
    
    # ===== UPDATE DESCRIPTION =====
    elif command == "update":
        if len(args) < 2:
            return json.dumps({
                "status": "error",
                "message": "Usage: update <id> <new_description>",
                "body": {}
            })
        task_id = args[0]
        new_description = " ".join(args[1:])
        return Update(task_id, new_description)
    
    # ===== DELETE TASK =====
    elif command == "delete":
        if not args:
            return json.dumps({
                "status": "error",
                "message": "Usage: delete <id>",
                "body": {}
            })
        task_id = args[0]
        return Delete(task_id)
    
    # ===== HELP =====
    elif command == "help":
        return Help()
    
    # ===== CLEAN ALL =====
    elif command == "clean":
        return CleanHouse()
    
    # ===== EXIT =====
    elif command == "exit":
        return "exit"
    
    # ===== UNKNOWN COMMAND =====
    else:
        return json.dumps({
            "status": "error",
            "message": f"Unknown command: {command}. Type 'help' for available commands.",
            "body": {}
        })

__all__ = ["router"]