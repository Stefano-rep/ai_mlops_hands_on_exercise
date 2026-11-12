FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --only-group backend --no-install-project
COPY src/backend ./src/backend
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
