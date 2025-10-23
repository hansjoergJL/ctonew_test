from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language question to answer from the Markdown knowledge base.")
    limit: Optional[int] = Field(None, ge=1, le=20, description="Maximum number of relevant excerpts to return.")


class Match(BaseModel):
    excerpt: str = Field(..., description="Relevant excerpt from the Markdown source text.")
    relevance: float = Field(..., ge=0, le=1, description="Cosine similarity score between 0 and 1.")
    index: int = Field(..., ge=0, description="Monotonic index of the excerpt within the source document.")


class QueryResponse(BaseModel):
    question: str
    matches: List[Match]
    source: str = Field(..., description="Absolute path to the Markdown knowledge base that was searched.")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the supported deployment environments?",
                "matches": [
                    {
                        "excerpt": "## Deployment\nOur service supports both Docker and native Linux deployments...",
                        "relevance": 0.82,
                        "index": 4,
                    }
                ],
                "source": "/opt/mcp/knowledge_base.md",
            }
        }
