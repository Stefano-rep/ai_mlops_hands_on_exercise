FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --only-group agent --no-install-project
COPY ai/agent ./ai/agent
RUN useradd --create-home appuser
USER appuser
ENV PYTHONUNBUFFERED=1
ENV AGENT_INTERFACE=cli
ENTRYPOINT ["/app/.venv/bin/python", "-m", "ai.agent"]
