from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .knowledge_base import ChunkMatch, MarkdownKnowledgeBase


@dataclass(slots=True)
class QueryResult:
    question: str
    matches: List[ChunkMatch]


class MarkdownQueryService:
    """Coordinates queries against the Markdown knowledge base."""

    def __init__(
        self,
        knowledge_base: MarkdownKnowledgeBase,
        *,
        default_top_k: int,
        max_top_k: int,
    ) -> None:
        self._knowledge_base = knowledge_base
        self._default_top_k = default_top_k
        self._max_top_k = max_top_k

    def query(self, question: str, *, limit: int | None = None) -> QueryResult:
        top_k = limit if limit is not None else self._default_top_k
        top_k = max(1, min(top_k, self._max_top_k))
        matches = self._knowledge_base.search(question, top_k=top_k)
        return QueryResult(question=question, matches=matches)
