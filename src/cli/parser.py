import json

from src.logic.task import Create_task, List, Status, Update, Delete, Help, CleanHouse

def router(inp:str):
    x = inp.split(" ")
    raw = x[1:]

    if (x[0] ==  "add"):
        message= ""
        for mesg in raw:
            message += mesg+" "

        addTask = Create_task(message)
        return addTask
    elif (x[0] == "list"):
        if len(raw) == 0:
            return List("all")
        elif raw[0] == "--todo":
            return List("todo")
        
        elif raw[0] == "--done":
            return List("done")
        
        elif raw[0] == "--progress":
            return List("progress")
        
    elif (x[0] == "status"):
        id = raw[0]
        status = raw[1]
        return Status(id, status)
    
    elif (x[0] == "update"):
        id = raw[0]
        message= ""
        for mesg in raw[1:]:
            message += mesg+" "
        return Update(id, message)
    
    elif (x[0] == "delete"):
        id = raw[0]
        return Delete(id)
    
    elif (x[0] == "help"):
        return Help()
    
    elif (x[0] == "exit"):
        return "exit"
    
    elif (x[0] == "clean"):
        return CleanHouse()
    
    else:
        print("unknown rule")


__all__ = ["router"]