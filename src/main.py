import json
from src.cli.parser import router
from src.data.repository import CreateDB
from src.logic.task import  List
import os
from src.data.db import init_db, get_connection

# ANSI colour codes
CYAN      = "\033[96m"
GREEN     = "\033[92m"
YELLOW    = "\033[93m"
RED       = "\033[91m"
WHITE     = "\033[97m"
MAGENTA   = "\033[95m"
BOLD      = "\033[1m"
RESET     = "\033[0m"

def format_output(raw_response):
    """Turn a router response into a styled string (handles dicts and lists)."""

    # ----- lists of tasks (direct list or JSON string) -----
    if isinstance(raw_response, list):
        tasks = raw_response
    elif isinstance(raw_response, str):
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, list):
                tasks = parsed
            else:
                # it's a dict – process below
                return format_dict_output(parsed)
        except (json.JSONDecodeError, TypeError):
            # not JSON, plain string
            return f"{WHITE}{raw_response}{RESET}"
    else:
        # other types: just show as text
        if isinstance(raw_response, dict):
            return format_dict_output(raw_response)
        return f"{WHITE}{raw_response}{RESET}"

    # ----- We have a list of tasks -----
    if not tasks:
        return f"{YELLOW}📭 No tasks found.{RESET}"

    # Table header
    header = f"{BOLD}{WHITE}{'ID':<28} {'Description':<48} {'Status':<15} {'Created'}{RESET}"
    separator = "─" * (28 + 1 + 48 + 1 + 15 + 1 + 10)

    lines = [header, separator]

    for task in tasks:
        tid      = task.get("id", "")
        desc     = task.get("description", "")
        status   = task.get("status", "")
        created  = task.get("created_at", "")[:10]   # YYYY-MM-DD

        # Truncate description if needed
        if len(desc) > 48:
            desc = desc[:45] + "..."

        # Style status
        if status == "DONE":
            icon, color = "✅", GREEN
        elif status == "IN_PROGRESS":
            icon, color = "⏳", YELLOW
        elif status == "TODO":
            icon, color = "☑️", CYAN
        else:
            icon, color = "", WHITE

        status_str = f"{icon} {status}"
        row = f"{tid:<28} {desc:<48} {color}{status_str:<15}{RESET} {created}"
        lines.append(row)

    return "\n".join(lines)


def format_dict_output(data: dict) -> str:
    """Format a single command response (add, update, delete, status change)."""
    status  = data.get("status", "")
    message = data.get("message", "")
    body    = data.get("body", {})

    if status == "success":
        icon, colour = "✅", GREEN
    elif status == "error":
        icon, colour = "❌", RED
    else:
        icon, colour = "ℹ️", CYAN

    lines = [f"{colour}{BOLD}{icon} {message}{RESET}"]

    if body:
        if "task" in body:
            lines.append(f"   {YELLOW}Task:{RESET} \"{body['task'].strip()}\"")
        if "status" in body:
            lines.append(f"   {YELLOW}Status:{RESET} {body['status']}")

    return "\n".join(lines)


def HandleUser():
    WELCOME = f"""
{CYAN}{BOLD}
      _______
     / TODO /,
    /      //
   /______//
  (______(/
{RESET}
{YELLOW}╔══════════════════════════════════════════════╗
║      📖  WELCOME TO YOUR TODO APP  📖         ║
╠══════════════════════════════════════════════╣
║                                              ║
║  ✏️  {GREEN} add <desc>                  {YELLOW}→ Create   ║
║  📋  {GREEN} list                        {YELLOW}→ List all  ║
║  ☑️  {GREEN} list --todo                 {YELLOW}→ TODO      ║
║  ⏳  {GREEN} list --progress             {YELLOW}→ IN_PROGRESS║
║  ✅  {GREEN} list --done                 {YELLOW}→ DONE      ║
║  🔄  {GREEN} status <id> <status>        {YELLOW}→ Change status║
║  📝  {GREEN} update <id> <desc>          {YELLOW}→ Edit desc  ║
║  🗑️  {GREEN} delete <id>                {YELLOW}→ Delete     ║
║  🧹  {GREEN} clean                        {YELLOW}→ Clear all tasks ║
║  ❓  {GREEN} help                        {YELLOW}→ Show help  ║
║  🚪  {GREEN}exit                                {YELLOW}cl→ Quit app   ║
║                                              ║
╚══════════════════════════════════════════════╝{RESET}
"""
    print(WELCOME)

    while True:
        user_input = input(f"{BOLD}> {RESET}").strip()
        if user_input.lower() == "exit":
            print(f"\n{GREEN}📕 Closing your book. Have a productive day!{RESET}")
            break
        

            

        response = router(user_input)
        if response is None or not response:
            print(f"{RED}⚠️  Please try again.{RESET}")
        else:
            print(format_output(response))
            print()  # extra spacing

if __name__ == "__main__":
    # Create both postgreSQL table and JSON file if they don't exist. This ensures the app is ready to use on first run, even if the database connection fails.
    init_db()
    if not os.path.exists("tasks.json"):
        CreateDB()
    HandleUser()