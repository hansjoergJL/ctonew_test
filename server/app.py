from __future__ import annotations

from fastapi import FastAPI

from .config import Settings
from .models import Match, QueryRequest, QueryResponse
from .service import MarkdownQueryService


def create_app(service: MarkdownQueryService, settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Markdown Lookup MCP Server",
        description=(
            "An MCP-compatible HTTP service that surfaces relevant excerpts "
            "from a Markdown knowledge base."
        ),
        version="1.0.0",
    )

    @app.get("/healthz", tags=["system"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/query", response_model=QueryResponse, tags=["query"])
    def query_markdown(request: QueryRequest) -> QueryResponse:
        result = service.query(request.question, limit=request.limit)
        matches = [
            Match(
                excerpt=_normalize_excerpt(match.text),
                relevance=round(match.score, 6),
                index=match.index,
            )
            for match in result.matches
        ]
        return QueryResponse(
            question=result.question,
            matches=matches,
            source=str(settings.knowledge_base_path),
        )

    return app


def _normalize_excerpt(text: str) -> str:
    collapsed = " ".join(segment.strip() for segment in text.splitlines() if segment.strip())
    return collapsed.strip()
