"""Read-only lexical search over the supplied synthetic product catalog."""
from __future__ import annotations
import csv
import os
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

def search_products(query: str, limit: int = 4) -> list[dict[str, str]]:
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        return []
    path = Path(configured).expanduser().resolve() / "data" / "products.csv"
    if not path.is_file():
        return []
    terms = {token.casefold() for token in TOKEN_RE.findall(query)}
    if not terms:
        return []
    scored = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            sku = (row.get("sku") or "").casefold()
            title = (row.get("title") or "").casefold()
            brand = (row.get("brand") or "").casefold()
            haystack = set(TOKEN_RE.findall(" ".join(row.values())))
            exact_sku = sku and sku in query.casefold()
            overlap = len(terms & haystack)
            if exact_sku or overlap:
                score = 100 if exact_sku else overlap
                scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [dict(row) for score, row in scored[:max(1, limit)]]
