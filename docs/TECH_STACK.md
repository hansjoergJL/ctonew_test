# Technical Overview

This document summarizes the technologies used by the Markdown Lookup MCP Server and explains why they were selected.

## Languages and Runtime

- **Python 3.11** — Primary implementation language. Modern syntax, excellent ecosystem support, and available by default on Ubuntu 22.04.

## Application Framework

- **FastAPI** — Provides declarative route definitions, request validation, and auto-generated OpenAPI documentation. FastAPI is the de facto standard for modern asynchronous Python APIs and integrates cleanly with Uvicorn.
- **Uvicorn** — ASGI web server that hosts the FastAPI application. Supports async I/O, hot reloading in development, and production-grade performance when paired with workers.

## Data Processing

- **Custom TF-IDF Engine** — Implemented in `server/knowledge_base.py`. Loading external vector databases or embedding services would introduce additional cost and operational complexity, so a bespoke implementation ensures predictable behavior and zero external dependencies.

## Supporting Libraries

- **Pydantic** — Validates and serializes request/response models.
- **Requests** — Used by the sample client to demonstrate HTTP access from Python.

## Project Structure

The codebase is split into focused modules to keep responsibilities clear:

- `server/config.py` — Environment-aware settings.
- `server/knowledge_base.py` — Markdown parsing, chunking, and vectorization.
- `server/service.py` — Coordinates query flow and safeguards limits.
- `server/app.py` — FastAPI application factory that wires the layers together.
- `server/main.py` — Entrypoint exposing `main()` and the ASGI `app` for Uvicorn.
- `sample/` — Example artifacts for exercising the API.

## Deployment Considerations

- Works on any Ubuntu 22.04 host with Python 3.11.
- No external services required — everything runs locally.
- Horizontal scaling can be achieved by running multiple Uvicorn workers behind a reverse proxy.
- Environment variables control runtime behavior, enabling twelve-factor friendly deployments.

## Testing and Validation

The repository includes a manual sample workflow in `sample/run_sample.py`. Automated tests can be added using pytest to cover the knowledge base chunking and scoring logic.
