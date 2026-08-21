from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def reset_tasks():
    # Keep tests independent by restoring the documented starter data.
    from app import main
    main.tasks[:] = [
        {"id": 1, "title": "Learn FastAPI", "done": True},
        {"id": 2, "title": "Build the task API", "done": False},
        {"id": 3, "title": "Write the README", "done": False},
    ]


def setup_function():
    reset_tasks()


def test_get_all_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_task_by_id():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_unknown_task():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "error" in response.json()["detail"]


def test_create_task():
    response = client.post("/tasks", json={"title": "Buy milk", "done": False})
    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"


def test_create_task_with_empty_title():
    response = client.post("/tasks", json={"title": "   ", "done": False})
    assert response.status_code == 400


def test_create_task_with_missing_title():
    response = client.post("/tasks", json={"done": False})
    assert response.status_code == 400


def test_update_task():
    response = client.put(
        "/tasks/1", json={"title": "Learn FastAPI deeply", "done": True}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Learn FastAPI deeply"


def test_update_task_with_empty_title():
    response = client.put("/tasks/1", json={"title": "", "done": True})
    assert response.status_code == 400


def test_update_unknown_task():
    response = client.put(
        "/tasks/999", json={"title": "Unknown", "done": False}
    )
    assert response.status_code == 404


def test_delete_task():
    response = client.delete("/tasks/3")
    assert response.status_code == 204
    assert client.get("/tasks/3").status_code == 404


def test_delete_unknown_task():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
