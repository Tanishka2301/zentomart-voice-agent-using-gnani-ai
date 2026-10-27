"""Lightweight retrieval over the supplied Markdown knowledge base.

This first version uses lexical TF-IDF-style scoring so it works without a
separate embedding service. It preserves section IDs and source paths for
grounded answers and evaluation. It is intentionally not a replacement for
testing retrieval against the capstone's gold_evidence labels.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
SECTION_RE = re.compile(r"\[([A-Za-z0-9_-]+)\]")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


@dataclass(frozen=True)
class Chunk:
    source: str
    section_id: str
    text: str
    terms: Counter[str]


class KnowledgeBase:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.document_frequency: Counter[str] = Counter()
        for chunk in chunks:
            self.document_frequency.update(chunk.terms.keys())
        self.total_documents = max(1, len(chunks))

    @classmethod
    def from_directory(cls, directory: str | Path, chunk_words: int = 180) -> "KnowledgeBase":
        root = Path(directory)
        if not root.exists():
            raise FileNotFoundError(f"Knowledge-base directory not found: {root}")
        paths = sorted(root.rglob("*.md"))
        if not paths:
            raise FileNotFoundError(
                f"No Markdown knowledge-base files found in {root}. "
                "Extract the supplied dataset and point --kb-dir to its kb folder."
            )

        chunks: list[Chunk] = []
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            # Split by headings where possible, then subdivide long sections.
            sections = re.split(r"(?m)(?=^#{1,6}\s+)", text)
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                match = SECTION_RE.search(section)
                section_id = match.group(1) if match else path.stem
                words = section.split()
                for start in range(0, len(words), chunk_words):
                    part = " ".join(words[start:start + chunk_words]).strip()
                    if part:
                        chunks.append(Chunk(
                            source=str(path.as_posix()),
                            section_id=section_id,
                            text=part,
                            terms=Counter(tokenize(part)),
                        ))
        return cls(chunks)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []
        scored: list[tuple[Chunk, float]] = []
        for chunk in self.chunks:
            score = 0.0
            for term, q_count in query_terms.items():
                tf = chunk.terms.get(term, 0)
                if not tf:
                    continue
                df = self.document_frequency.get(term, 0)
                idf = math.log(1 + (self.total_documents - df + 0.5) / (df + 0.5))
                score += q_count * idf * (tf / (tf + 1.2))
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:max(1, top_k)]
