# Markdown Lookup MCP Server

A production-ready Model Context Protocol (MCP) server that answers questions by searching curated Markdown documentation. The service exposes a clean HTTP API, runs entirely on Ubuntu with open-source dependencies, and includes a sample client for quick integration testing.

## Features

- Fast TF-IDF based retrieval over a large Markdown file.
- Deterministic results without paid third-party services.
- Fully documented FastAPI interface with OpenAPI schema at `/docs` and `/openapi.json`.
- Environment-driven configuration for host, port, and knowledge base path.
- Sample client script for end-to-end validation.

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Runtime | Python 3.11 | Primary language and runtime |
| Web Framework | FastAPI | HTTP routing, validation, and OpenAPI generation |
| Server | Uvicorn | ASGI server used to host the FastAPI app |
| Data Processing | Custom TF-IDF implementation | Lightweight vector scoring over Markdown chunks |
| HTTP Client (sample) | Requests | Demonstrates how to call the API from Python |

Additional documentation is available in [`docs/TECH_STACK.md`](docs/TECH_STACK.md).

## Repository Layout

```
server/
  app.py               # FastAPI application factory
  config.py            # Environment-driven settings
  data/knowledge_base.md
                       # Primary Markdown knowledge base
  knowledge_base.py    # Markdown chunking and TF-IDF search implementation
  main.py              # Entrypoint exposing `main()` and the ASGI app
  models.py            # Pydantic request/response schemas
  service.py           # Query orchestration layer
sample/
  run_sample.py        # Client script that calls the MCP server
  test_question.txt    # Example query text
```

## Requirements

- Ubuntu 22.04 LTS or later
- Python 3.11+
- pip

All Python dependencies are listed in [`requirements.txt`](requirements.txt).

## Setup

1. **Clone and install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Run the server**
   ```bash
   python -m server.main
   ```
   The service defaults to `http://0.0.0.0:8000` and automatically loads the bundled knowledge base.

3. **Explore the API**
   - [Interactive Docs](http://localhost:8000/docs)
   - [OpenAPI JSON](http://localhost:8000/openapi.json)

4. **Query the server using the sample client**
   ```bash
   python sample/run_sample.py
   ```

## Configuration

Environment variables allow fine grained control without code changes:

- `MCP_SERVER_HOST` — Interface to bind (default: `0.0.0.0`).
- `MCP_SERVER_PORT` — Port to bind (default: `8000`).
- `KNOWLEDGE_BASE_PATH` — Override path to the Markdown file.
- `DEFAULT_TOP_K` — Default number of excerpts returned (default: `3`).
- `MAX_TOP_K` — Maximum number of excerpts returned per query (default: `8`).

## API Reference

### `POST /query`

Request body:

```json
{
  "question": "string",
  "limit": 3
}
```

- `question` *(required)* — Natural language question.
- `limit` *(optional)* — Maximum number of relevant excerpts (1-20). Defaults to the server configuration.

Response body:

```json
{
  "question": "...",
  "matches": [
    {
      "excerpt": "...",
      "relevance": 0.87,
      "index": 5
    }
  ],
  "source": "/absolute/path/to/knowledge_base.md"
}
```

### `GET /healthz`

Health probe returning `{ "status": "ok" }` when the service is operational.

## Running on Ubuntu

The server uses only open-source dependencies, so there are no recurring licensing costs. To deploy on Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv
python3 -m venv /opt/mcp/.venv
source /opt/mcp/.venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8080 --workers 2
```

Ensure the `knowledge_base.md` file is available on the host and update `KNOWLEDGE_BASE_PATH` if you relocate it.

## Sample Workflow

1. Run the server locally.
2. Execute `python sample/run_sample.py` to send the question in `sample/test_question.txt`.
3. Inspect the JSON response printed by the script.

## License

This project is released under the MIT License. Update `LICENSE` if your organization requires a different choice.
