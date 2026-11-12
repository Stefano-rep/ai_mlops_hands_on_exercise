# AI/MLops Hands-On Exercise

Each student picks **one dataset** from the catalogue below and carries it through the entire hands-on. Every task builds on the previous one, so code is reused and extended rather than rewritten.

Every task ends with a short report in Markdown, written in your own words.

To begin the exercise simply fork this repository.

## In this repository

In this repository you will find:

- a guide for each task;

- datasets description;

- AI usage rules;

- datasets.

## Build and run

Run the following commands from the repository root. Docker Desktop (or a
Docker Engine installation with Docker Compose) must be running.

Required local files:

- Full-stack application: `datasets/census_income_cleaned.csv`.
- Agent: `artifacts/mlp_pipeline.joblib`.

The `datasets/` directory is excluded from Git, so cloning the repository
does not provide the CSV files. Place them in `datasets/` before starting
the application. The model artifact must also be present before starting
the agent; see the training instructions below if it needs to be generated.

### FastAPI and React with Docker Compose

Build and start the backend and frontend:

```sh
docker compose build backend frontend
docker compose up -d backend frontend
```

Alternatively, build and start with a single command:

```sh
docker compose up --build -d
```

Open the application at http://localhost:8080 and the API documentation at
http://localhost:8080/api/docs. Nginx serves React and forwards `/api/` requests
to FastAPI. Set `APP_PORT` in a root `.env` file to change the published port.

Inspect logs or stop the services:

```sh
docker compose logs -f backend frontend
docker compose down
```

### Agent with Docker Compose (terminal interface)

Build the agent image, then start an interactive session:

```sh
docker compose --profile agent build agent
docker compose --profile agent run --rm agent
```

The full-stack application can remain running in another terminal. The agent
uses the offline mock provider by default and requires no real API key. Enter
`/schema` to inspect input fields, paste a complete JSON record to predict,
or enter `/quit` to exit. The temporary container is removed on exit.

Run a prediction using the bundled example without an interactive session:

```sh
docker compose --profile agent run --rm -T agent --input ai/agent/example_record.json
```

### Agent with Tkinter (local desktop interface)

The Tkinter window runs on the host, not inside Docker. It requires Python
3.12 with Tcl/Tk support and uv:

```sh
uv sync --group agent
uv run --group agent python -m ai.agent
```

Use **Load example**, then **Send** to try the MLP. The window also supports
JSON file loading, input schema lookup, provider selection and conversation
reset. See [the agent documentation](ai/agent/README.md) for OpenAI configuration
and additional commands. Only a fake API key is provided; OpenAI mode requires
your own key in the environment.

### Generate the model artifact

If `artifacts/mlp_pipeline.joblib` is missing, first provide
`datasets/census_income_training.csv`, then run locally:

```sh
uv sync
uv run python ai/ml/training/train.py
```

The training script compares the models and saves the fitted MLP pipeline,
including preprocessing, to `artifacts/mlp_pipeline.joblib`.
