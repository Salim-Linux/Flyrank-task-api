import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List

# Database file lives next to the app. Opening a missing file creates it.
DB_PATH = Path(__file__).resolve().parent.parent / "tasks.db"

app = FastAPI(
    title="FlyRank Task API",
    description="A simple CRUD REST API for managing tasks using SQLite storage.",
    version="1.0.0",
)


# ---------- Database helpers ----------

def get_connection() -> sqlite3.Connection:
    """Open a connection to tasks.db (created automatically if missing)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def init_db() -> None:
    """Create the tasks table if missing, and seed examples only when empty."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Learn FastAPI", 1),
                    ("Build the task API", 0),
                    ("Write the README", 0),
                ],
            )


def row_to_task(row: sqlite3.Row) -> dict:
    """Convert a database row into the task JSON shape."""
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


# Create the table + seed on startup.
init_db()


# ---------- Models ----------

class TaskCreate(BaseModel):
    title: str = Field(..., description="The task title")
    done: bool = False


class Task(TaskCreate):
    id: int


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    # FlyRank requires invalid request bodies to return 400, not FastAPI's default 422.
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request body"},
    )


def validate_title(title: str) -> str:
    if not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title cannot be empty"},
        )
    return title.strip()


@app.get("/tasks", response_model=List[Task], status_code=status.HTTP_200_OK)
def get_tasks():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def get_task(task_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"},
        )
    return row_to_task(row)


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    title = validate_title(task.title)
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 1 if task.done else 0),
        )
        new_id = cursor.lastrowid
    return {"id": new_id, "title": title, "done": task.done}


@app.put("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task: TaskCreate):
    title = validate_title(task.title)
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, 1 if task.done else 0, task_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found"},
            )
    return {"id": task_id, "title": title, "done": task.done}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found"},
            )
