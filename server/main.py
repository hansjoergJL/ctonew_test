from __future__ import annotations

import logging

import uvicorn

from .app import create_app
from .config import Settings
from .knowledge_base import MarkdownKnowledgeBase
from .service import MarkdownQueryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings.from_env()
logger.info("Loading knowledge base from %s", settings.knowledge_base_path)
knowledge_base = MarkdownKnowledgeBase(settings.knowledge_base_path)
service = MarkdownQueryService(
    knowledge_base,
    default_top_k=settings.default_top_k,
    max_top_k=settings.max_top_k,
)
app = create_app(service, settings)


def main() -> None:
    """Entry point for running the MCP server directly."""
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
