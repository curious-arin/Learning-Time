# Student Management Frontend

A simple HTML, CSS and JavaScript interface for your FastAPI student API.

## Run it

1. Start your FastAPI app from the directory containing `data.json`:
   `uvicorn main:app --reload`
2. Ensure the API is available at `http://127.0.0.1:8000` (or edit `API_BASE` in `app.js`).
3. Open this folder with VS Code Live Server, or serve it with:
   `python -m http.server 5500`
4. Visit `http://127.0.0.1:5500`.

## Important: enable CORS in FastAPI

Because the frontend and API run on different ports, add this to your FastAPI file after creating `app`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Backend fixes needed

Your update route reconstructs a `Student` model, which requires `id`, but the saved JSON record omits it. Change:

```python
student = Student(**existing)
```

to:

```python
student = Student(id=student_id, **existing)
```

Also change the missing-student status in `get_id` from `405` to `404`. Your root route should return a JSON object, e.g. `return {"message": "Welcome back Arin"}` rather than a Python set.
