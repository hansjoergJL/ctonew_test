"""Simple client script that queries the Markdown lookup MCP server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

DEFAULT_ENDPOINT = "http://localhost:8000/query"
DEFAULT_PROMPT_FILE = Path(__file__).with_name("test_question.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the Markdown MCP server")
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="HTTP endpoint for the MCP server (default: %(default)s)",
    )
    parser.add_argument(
        "--question-file",
        type=Path,
        default=DEFAULT_PROMPT_FILE,
        help="Path to a text file containing the question to ask",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit for the number of excerpts returned",
    )
    args = parser.parse_args()

    question_path: Path = args.question_file
    if not question_path.exists():
        raise SystemExit(f"Question file not found: {question_path}")

    question = question_path.read_text(encoding="utf-8").strip()
    if not question:
        raise SystemExit("Question file is empty")

    payload: dict[str, Any] = {"question": question}
    if args.limit is not None:
        payload["limit"] = args.limit

    response = requests.post(args.endpoint, json=payload, timeout=10)
    response.raise_for_status()

    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
