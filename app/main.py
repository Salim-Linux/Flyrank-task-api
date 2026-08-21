from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(
    title="FlyRank Task API",
    description="A simple CRUD REST API for managing tasks using in-memory storage.",
    version="1.0.0",
)

# In-memory storage. Data is reset whenever the server restarts.
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": True},
    {"id": 2, "title": "Build the task API", "done": False},
    {"id": 3, "title": "Write the README", "done": False},
]


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
    return tasks


@app.get("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "Task not found"},
    )


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    title = validate_title(task.title)
    next_id = max((item["id"] for item in tasks), default=0) + 1
    new_task = {"id": next_id, "title": title, "done": task.done}
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task: TaskCreate):
    title = validate_title(task.title)

    for index, existing_task in enumerate(tasks):
        if existing_task["id"] == task_id:
            updated_task = {
                "id": task_id,
                "title": title,
                "done": task.done,
            }
            tasks[index] = updated_task
            return updated_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "Task not found"},
    )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "Task not found"},
    )
