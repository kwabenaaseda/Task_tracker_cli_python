import psycopg2
import os
from datetime import datetime

# PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kwabenaaseda:logosyn%402020242914@localhost:5432/task_tracker"
)

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Create tasks table if it doesn't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'General',
                status VARCHAR(50) DEFAULT 'TODO',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

def format_time():
    """Return current time in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def READPS():
    """Read all tasks from database"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, description, category, status, created_at, updated_at FROM tasks ORDER BY created_at")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert to list of dicts (like the old JSON format)
        tasks = [
            {
                "id": str(row[0]),
                "description": row[1],
                "status": row[2],
                "category": row[3],
                "created_at": row[4].isoformat(),
                "updated_at": row[5].isoformat()
            }
            for row in rows
        ]
        
        return {
            "title": "TASK MANAGER",
            "owner": "kwabenaaseda",
            "created_at": format_time(),
            "updated_at": format_time(),
            "tasks": tasks
        }
    except Exception as e:
        print(f"Error reading tasks: {e}")
        return False

def WRITE(payload):
    """This is handled by individual INSERT/UPDATE/DELETE operations now"""
    # With a real database, we don't need to "write" the whole payload
    # Each operation commits individually
    return True

def SETUP():
    """Set up database and return tasks"""
    call = READPS()
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

def CLEARDB():
    """Delete all tasks from the database"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing tasks: {e}")
        return False




__all__ = ["SETUP", "format_time", "READPS", "WRITE", "init_db", "CLEARDB"]