"""FastAPI entry point."""

from fastapi import FastAPI

app = FastAPI(title="AI/MLops API", root_path="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/message")
def message() -> dict[str, str]:
    return {"message": "Hello from FastAPI!"}
