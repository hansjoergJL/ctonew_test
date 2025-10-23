from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Runtime configuration for the Markdown lookup MCP server."""

    host: str
    port: int
    knowledge_base_path: Path
    default_top_k: int
    max_top_k: int

    @classmethod
    def from_env(cls) -> "Settings":
        base_dir = Path(__file__).resolve().parent
        host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_SERVER_PORT", "8000"))
        knowledge_base_env = os.getenv("KNOWLEDGE_BASE_PATH")
        if knowledge_base_env:
            knowledge_base_path = Path(knowledge_base_env)
            if not knowledge_base_path.is_absolute():
                knowledge_base_path = (base_dir / knowledge_base_path).resolve()
        else:
            knowledge_base_path = (base_dir / "data" / "knowledge_base.md").resolve()

        default_top_k = int(os.getenv("DEFAULT_TOP_K", "3"))
        max_top_k = int(os.getenv("MAX_TOP_K", "8"))
        default_top_k = max(1, min(default_top_k, max_top_k))

        return cls(
            host=host,
            port=port,
            knowledge_base_path=knowledge_base_path,
            default_top_k=default_top_k,
            max_top_k=max_top_k,
        )
