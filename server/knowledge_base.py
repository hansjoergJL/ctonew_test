from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

_TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9']+")
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}


@dataclass(slots=True)
class Chunk:
    index: int
    text: str
    tokens: Sequence[str]
    term_freq: Counter[str]
    weights: dict[str, float]
    norm: float


@dataclass(slots=True)
class ChunkMatch:
    text: str
    score: float
    index: int


class MarkdownKnowledgeBase:
    """Load and query Markdown content using a lightweight TF-IDF search."""

    def __init__(
        self,
        source_path: Path,
        *,
        min_chunk_chars: int = 220,
        max_chunk_chars: int = 900,
    ) -> None:
        self.source_path = source_path
        self.min_chunk_chars = min_chunk_chars
        self.max_chunk_chars = max_chunk_chars
        self._chunks: List[Chunk] = []
        self._idf: dict[str, float] = {}
        self._load()

    def _load(self) -> None:
        if not self.source_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {self.source_path}")

        raw_text = self.source_path.read_text(encoding="utf-8")
        chunk_texts = self._chunk_markdown(raw_text)
        temp_chunks: List[tuple[int, str, Sequence[str], Counter[str]]] = []
        document_frequency: Counter[str] = Counter()

        for idx, text in enumerate(chunk_texts):
            tokens = tuple(self._tokenize(text))
            if not tokens:
                continue
            term_freq = Counter(tokens)
            temp_chunks.append((idx, text, tokens, term_freq))
            document_frequency.update(set(tokens))

        if not temp_chunks:
            raise ValueError("Knowledge base is empty after processing.")

        total_docs = len(temp_chunks)
        self._idf = {
            token: math.log((1 + total_docs) / (1 + df)) + 1.0
            for token, df in document_frequency.items()
        }
        default_idf = math.log(1 + total_docs) + 1.0

        chunks: List[Chunk] = []
        for idx, text, tokens, term_freq in temp_chunks:
            vector: dict[str, float] = {}
            token_count = len(tokens)
            for token, freq in term_freq.items():
                idf = self._idf.get(token, default_idf)
                tf = freq / token_count
                vector[token] = tf * idf
            norm = math.sqrt(sum(weight * weight for weight in vector.values())) or 1.0
            chunks.append(
                Chunk(
                    index=idx,
                    text=text,
                    tokens=tokens,
                    term_freq=term_freq,
                    weights=vector,
                    norm=norm,
                )
            )

        self._chunks = chunks

    def search(self, query: str, *, top_k: int = 3) -> List[ChunkMatch]:
        query_tokens = tuple(self._tokenize(query))
        if not query_tokens:
            return []

        query_tf = Counter(query_tokens)
        token_count = len(query_tokens)
        query_vector: dict[str, float] = {}
        for token, freq in query_tf.items():
            idf = self._idf.get(token)
            if idf is None:
                continue
            tf = freq / token_count
            query_vector[token] = tf * idf

        if not query_vector:
            return []

        query_norm = math.sqrt(sum(weight * weight for weight in query_vector.values())) or 1.0

        scored: List[ChunkMatch] = []
        for chunk in self._chunks:
            dot = 0.0
            for token, weight in query_vector.items():
                chunk_weight = chunk.weights.get(token)
                if chunk_weight:
                    dot += chunk_weight * weight
            if dot <= 0:
                continue
            score = dot / (chunk.norm * query_norm)
            scored.append(ChunkMatch(text=chunk.text, score=score, index=chunk.index))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _chunk_markdown(self, raw_text: str) -> List[str]:
        lines = raw_text.splitlines()
        chunks: List[str] = []
        buffer: List[str] = []
        char_count = 0

        def flush_buffer() -> None:
            nonlocal buffer, char_count
            if buffer:
                chunk = "\n".join(buffer).strip()
                if chunk:
                    chunks.append(chunk)
            buffer = []
            char_count = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if char_count >= self.min_chunk_chars:
                    flush_buffer()
                else:
                    buffer.append("")
                continue

            if stripped.startswith("#") and char_count >= self.min_chunk_chars:
                flush_buffer()

            buffer.append(stripped)
            char_count += len(stripped)

            if char_count >= self.max_chunk_chars:
                flush_buffer()

        if buffer:
            flush_buffer()

        return chunks

    def _tokenize(self, text: str) -> Iterable[str]:
        for match in _TOKEN_PATTERN.finditer(text.lower()):
            token = match.group(0)
            if token in _STOP_WORDS:
                continue
            yield token
