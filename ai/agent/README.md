# Census desktop and CLI agent

## Desktop interface (default local startup)

```sh
uv sync --group agent
uv run --group agent python -m ai.agent
```

The Tkinter window provides a chat, provider selection, JSON file loading,
a bundled example, input schema lookup and conversation reset. Press Send or
Ctrl+Enter to submit. Requests run in a background thread so the window stays
responsive. Mock mode works offline; OpenAI uses the existing environment
configuration. No API key is stored in the interface.

Tkinter is part of Python's standard library, not a pip/uv package. It needs
a desktop session and a Python installation with Tcl/Tk support (on Debian/
Ubuntu, install the matching `python3-tk` system package if missing).
Docker Compose retains the CLI because the container has no desktop display;
run the graphical interface directly on the host.

LangGraph orchestrates `assistant -> tools -> assistant`. The tool loads the
original fitted MLP pipeline, including preprocessing, from
`artifacts/mlp_pipeline.joblib`. It does not retrain the model or require the
training CSV. The artifact expects the training feature format, including the
already encoded race, sex and occupation columns.

## Run with Docker Compose

From the repository root, with Docker running:

```sh
docker compose --profile agent build agent
docker compose --profile agent run --rm agent
```

The agent profile is optional, so the web application's default startup is
unchanged. The model is mounted read-only. To run a complete prediction using
the bundled example, without an interactive terminal:

```sh
docker compose --profile agent run --rm -T agent --input ai/agent/example_record.json
```

## Local CLI

```sh
uv sync --group agent
uv run --group agent python -m ai.agent --cli
uv run --group agent python -m ai.agent --input ai/agent/example_record.json
uv run --group agent python -m ai.agent --message /schema
```

Interactive commands: `/schema` shows required fields and category values,
`/reset` clears conversation history, and `/quit` exits. Paste a complete JSON
record on one line to predict, or use `--input` with a JSON file. Class `0`
means `<=50K`, class `1` means `>50K`. Probabilities come directly from the MLP.

The default `mock` provider is a deterministic stand-in, not a real language
model: it converts JSON input into a tool call and prints the tool result.
It makes no OpenAI requests and requires no valid API key.

## OpenAI mode

Copy `ai/agent/.env.example` to the repository root as `.env` (merge the values
if that file already exists). Set `AGENT_PROVIDER=openai` and replace the fake
key with your own `OPENAI_API_KEY`. `OPENAI_MODEL` selects a tool-capable model
available to your account. No real credentials are included in the repository.
Compose loads the root `.env`; local execution reads environment variables,
so export them in your shell or use uv's `--env-file .env` option:

```sh
uv run --env-file .env --group agent python -m ai.agent
docker compose --profile agent run --rm agent
```

OpenAI mode supports natural-language conversations and tool calling. It asks
for missing input values rather than inventing them. The placeholder key is
rejected before a network request. Real-provider requests require a valid key
and may incur API charges; this mode is configured but not live-tested.

Set `ML_MODEL_PATH` to override the artifact path locally. To regenerate the
artifact, run `uv run python ai/ml/training/train.py` at the repository root.

References: [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart),
[ChatOpenAI tool calling](https://docs.langchain.com/oss/python/integrations/chat/openai),
[OpenAI authentication](https://developers.openai.com/api/reference/overview).
