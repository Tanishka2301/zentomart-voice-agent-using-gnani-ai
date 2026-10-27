"""Policy-aware lexical retrieval for Markdown knowledge-base documents."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[^\W_]+", re.IGNORECASE | re.UNICODE)
SECTION_RE = re.compile(r"^##\s*\[([A-Za-z0-9_.-]+)\]", re.MULTILINE)
META_RE = re.compile(r"(?m)^([a-z_]+):\s*(.*?)\s*$")

@dataclass(frozen=True)
class Chunk:
    source: str
    section_id: str
    text: str
    terms: Counter[str]
    doc_type: str = "unknown"
    status: str = "current"

def tokenize(text: str) -> list[str]:
    # Normalize common Devanagari nukta variants so equivalent spellings match.
    text = text.replace("\u093c", "")
    return [token.lower() for token in TOKEN_RE.findall(text)]

QUERY_EXPANSIONS = {
    "रिफंड": ("refund",), "रिफ़ंड": ("refund",),
    "मेरा": ("my",), "मेरी": ("my",), "मेरे": ("my",),
    "कहाँ": ("where", "status"), "कहां": ("where", "status"),
    "पैसा": ("money",), "पैसे": ("money",),
    "वापस": ("return",), "वापसी": ("return",),
    "ऑर्डर": ("order",), "आर्डर": ("order",),
    "डिलीवरी": ("delivery",), "पिनकोड": ("pincode",),
    "आखिरी": ("last", "digits"), "आख़िरी": ("last", "digits"),
    "अंक": ("digits",), "चार": ("four",), "दिन": ("days",),
    "कितने": ("how", "many"), "मिला": ("received",),
    "मिले": ("received",), "आया": ("arrived",), "आए": ("arrived",),
    "नहीं": ("not",), "है": ("is",), "हैं": ("are",),
    "mera": ("my",), "meri": ("my",), "mere": ("my",),
    "kahan": ("where", "status"), "paisa": ("money",),
    "paise": ("money",), "wapas": ("return",), "kitne": ("how", "many"),
    "din": ("days",), "nahi": ("not",), "mila": ("received",),
    "aaya": ("arrived",), "hain": ("are",), "hai": ("is",),
}

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
            raise FileNotFoundError(f"No Markdown knowledge-base files found in {root}.")
        chunks: list[Chunk] = []
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            metadata_match = re.search(r"(?s)^---\s*\n(.*?)\n---", text)
            metadata = dict(META_RE.findall(metadata_match.group(1))) if metadata_match else {}
            status = metadata.get("status", "current").strip().lower()
            doc_type = metadata.get("doc_type", "unknown").strip().lower()
            # Superseded documents must never compete with current policy.
            if status == "superseded":
                continue
            sections = re.split(r"(?m)(?=^#{1,6}\s+)", text)
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                match = SECTION_RE.search(section)
                section_id = match.group(1) if match else path.stem
                words = section.split()
                for start in range(0, len(words), max(1, chunk_words)):
                    part = " ".join(words[start:start + max(1, chunk_words)]).strip()
                    if part:
                        chunks.append(Chunk(
                            source=str(path.as_posix()), section_id=section_id,
                            text=part, terms=Counter(tokenize(part)),
                            doc_type=doc_type, status=status,
                        ))
        return cls(chunks)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        query_tokens = tokenize(query)
        expanded_tokens = list(query_tokens)
        for token in query_tokens:
            expanded_tokens.extend(QUERY_EXPANSIONS.get(token, ()))
        normalized_query = query.replace("\\u093c", "").casefold()
        for source, expansions in QUERY_EXPANSIONS.items():
            normalized_source = source.replace("\\u093c", "").casefold()
            if any("\\u0900" <= char <= "\\u097f" for char in normalized_source):
                matched = normalized_source in normalized_query
            else:
                matched = bool(re.search(r"\\b" + re.escape(normalized_source) + r"\\b", normalized_query))
            if matched:
                expanded_tokens.extend(expansions)
        query_terms = Counter(expanded_tokens)
        if not query_terms:
            return []
        scored: list[tuple[Chunk, float]] = []
        priority = {"policy": 1.35, "agent_guide": 1.2, "help": 1.05, "faq": 1.0, "marketing": 0.7}
        for chunk in self.chunks:
            score = 0.0
            for term, q_count in query_terms.items():
                tf = chunk.terms.get(term, 0)
                if tf:
                    df = self.document_frequency.get(term, 0)
                    idf = math.log(1 + (self.total_documents - df + 0.5) / (df + 0.5))
                    score += q_count * idf * (tf / (tf + 1.2))
            score *= priority.get(chunk.doc_type, 1.0)
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:max(1, top_k)]
