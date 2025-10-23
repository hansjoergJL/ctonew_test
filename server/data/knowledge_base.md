# Platform Operations Handbook

This handbook contains guidance for engineers operating the Markdown lookup MCP server.
It covers architecture, deployment, observability, security, and routine operational tasks.

## System Overview

The Markdown lookup MCP server provides a knowledge retrieval layer that indexes internal documentation stored as Markdown.
Clients submit a natural language question to the `/query` endpoint, and the service responds with the most relevant excerpts.
The service is stateless and resilient to restarts because it can rebuild its in-memory index on launch.

### Key Capabilities

- Fast lookup over curated Markdown documentation.
- Lightweight TF-IDF ranking with cosine similarity.
- Configurable number of excerpts returned to the caller.
- Deterministic, repeatable results without relying on third-party paid APIs.
- Secure by default with no stateful user data.

### Non-Goals

- The service does not persist chat histories.
- The service does not modify the Markdown files at runtime.
- The service is not intended to be a replacement for full-text enterprise search.

## Architecture

The runtime architecture has three primary layers:

1. **HTTP Interface** — Exposed via FastAPI, providing OpenAPI documentation and JSON responses.
2. **Query Service** — Orchestrates request validation, result limits, and the scoring pipeline.
3. **Knowledge Base** — Loads and indexes Markdown documentation at boot time, computing TF-IDF vectors per excerpt.

The server relies solely on standard Linux capabilities and open-source Python libraries so it can run cost-effectively on commodity Ubuntu hosts.

## Deployment

Deployments must target Ubuntu 22.04 LTS or later. Python 3.11 is the recommended runtime because it offers strong performance and matches the default version in most modern distributions.

### Local Development

1. Create a Python virtual environment using `python3 -m venv .venv`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the server with `python -m server.main`.
4. Issue test queries using the sample script in the `sample` directory.

### Production Rollout

1. Provision a dedicated Ubuntu instance with at least 2 vCPUs and 4 GB of RAM.
2. Install system packages: `sudo apt-get update && sudo apt-get install python3 python3-venv`.
3. Copy the repository to the host and create a Python virtual environment.
4. Install Python dependencies from `requirements.txt`.
5. Launch the service with `uvicorn server.main:app --host 0.0.0.0 --port 8080 --workers 2` managed by a process supervisor such as systemd.
6. Place the Markdown knowledge base under `server/data/knowledge_base.md` or configure the `KNOWLEDGE_BASE_PATH` environment variable.

## Configuration

All configuration is environment driven:

- `MCP_SERVER_HOST`: IP address to bind the HTTP server. Defaults to `0.0.0.0`.
- `MCP_SERVER_PORT`: TCP port for the HTTP server. Defaults to `8000`.
- `KNOWLEDGE_BASE_PATH`: Absolute or relative path to the Markdown knowledge base. Defaults to the bundled data file.
- `DEFAULT_TOP_K`: Default number of excerpts returned when the client does not specify a limit. Defaults to `3`.
- `MAX_TOP_K`: Upper bound on excerpts returned per query. Defaults to `8`.

## Query Processing Pipeline

1. The FastAPI layer validates the incoming JSON payload.
2. The query service clamps the requested limit to a safe range.
3. The knowledge base tokenizes the question and generates a TF-IDF vector in-place.
4. Each Markdown chunk has a pre-computed TF-IDF vector, normalized to unit length.
5. The system performs cosine similarity scoring and sorts the results.
6. The top-ranked excerpts are returned to the caller together with their scores.

### Tokenization Rules

- Tokens must start with a letter and can include alphanumeric characters and apostrophes.
- Common English stop words are excluded from the TF-IDF representation.
- Tokens are normalized to lowercase.

### Chunk Sizing

- Sections are accumulated until they reach approximately 220 characters.
- Any chunk that grows past 900 characters is flushed to maintain responsiveness.
- Headings begin new chunks when the accumulated content is sufficiently large.

## Observability

Logging is handled through the standard Python logging module.
At startup the service logs the source path of the loaded knowledge base.
Additional instrumentation can be layered on top using FastAPI middleware when needed.

## Security Considerations

- The Markdown files should not contain sensitive credentials or secrets.
- Deployments should restrict inbound network access to trusted clients.
- Use HTTPS termination via a reverse proxy in production environments.

## Maintenance

- Keep the Markdown knowledge base accurate and well-structured because the search quality depends on content quality.
- Review dependency updates quarterly to stay on supported versions of FastAPI and Uvicorn.
- Back up the Markdown files alongside other documentation assets.

## Troubleshooting

| Symptom | Possible Cause | Resolution |
| --- | --- | --- |
| Queries return no results | Knowledge base path incorrect or empty | Confirm `KNOWLEDGE_BASE_PATH` and file contents |
| Slow responses | Host under-provisioned | Increase CPU/RAM or reduce chunk size |
| HTTP 422 errors | Invalid JSON payload | Ensure the request body matches the OpenAPI schema |

## Frequently Asked Questions

**Q: Can the service search multiple Markdown files?**
A: The reference implementation supports a single Markdown file. Combine multiple files into one, or extend the loader to accept a directory.

**Q: How do we update the knowledge base?**
A: Edit the Markdown file and deploy a refreshed build. The service reloads the file at startup, so a restart is required to pick up changes.

**Q: Does the service support embeddings or vector databases?**
A: The default implementation uses deterministic TF-IDF scoring. Embeddings are out of scope for this release but can be added later.

**Q: What is the expected response shape?**
A: Responses contain the original question, a list of excerpts with relevance scores, and the source Markdown path.

**Q: Can it run offline?**
A: Yes. The service has no external API dependencies.

**Q: How large can the Markdown file be?**
A: Files up to a few megabytes perform well on standard hardware. For larger corpora consider more advanced indexing strategies.

## Glossary

- **Excerpt** — A contiguous piece of Markdown consolidated for relevance scoring.
- **TF-IDF** — Term Frequency-Inverse Document Frequency, a weighting scheme for assessing importance of tokens.
- **Cosine Similarity** — A metric for measuring the angle between two vectors, used to determine relevance.
- **MCP** — Model Context Protocol, allowing structured knowledge retrieval for assistants and agents.

## Release Process

1. Merge tested changes to the main branch.
2. Tag a new version following semantic versioning.
3. Build and publish a container image if applicable.
4. Update deployment manifests referencing the new version.
5. Perform a canary release before full rollout.

## Contact

- **Team**: Platform Enablement
- **Email**: platform@example.com
- **Escalation**: PagerDuty rotation `platform-oncall`

---

_Last reviewed: September 2024_
