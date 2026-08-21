# FlyRank Task API

A small REST API built with **Python + FastAPI** for the FlyRank CRUD assignment.

The API stores tasks in an **in-memory list**. There is no database and no file-based persistence.

## Requirements

- Python 3.10+
- pip

## Run the API

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server with one command:

```bash
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Endpoint table

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/tasks` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200 |
| POST | `/tasks` | Create a task | 201 |
| PUT | `/tasks/{id}` | Replace a task | 200 |
| DELETE | `/tasks/{id}` | Delete a task | 204 |

### Error behavior

- Invalid or missing request body/title: **400**
- Unknown task ID: **404**
- Errors return a JSON error message.

## Example request bodies

Create:

```json
{
  "title": "Buy milk",
  "done": false
}
```

Update:

```json
{
  "title": "Buy milk",
  "done": true
}
```

## curl examples

List tasks:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Get one task:

```bash
curl -i http://127.0.0.1:8000/tasks/1
```

Create:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{"title":"Buy milk","done":false}"
```

Update:

```bash
curl -i -X PUT http://127.0.0.1:8000/tasks/1 -H "Content-Type: application/json" -d "{"title":"Learn FastAPI deeply","done":true}"
```

Delete:

```bash
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```

## Testing

Run:

```bash
pytest
```

## Persistence note

The tasks are stored only in memory. Restarting the server resets the list to the three example tasks defined in `app/main.py`. This means data created during a run does not survive a server restart.

## Swagger screenshot

Add the required screenshot of `/docs` here before submitting the project.

## AI vs me

This section is for **Stage 7**. The hand-built implementation above should remain the Stage 0–6 submission. For Stage 7, place the AI-generated version in `ai-version/` or a separate branch and document the comparison here.

Include:

1. The full prompt you wrote.
2. What the AI did better.
3. What the AI got wrong or ignored.
4. What your prompt failed to specify.
5. At least three concrete differences.
6. One sentence describing what changed after the rematch.
