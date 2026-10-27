"""Read-only lexical search over the supplied synthetic product catalog."""
from __future__ import annotations
import csv
import os
import re
import unicodedata
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


def lookup_pincodes(query: str) -> list[dict[str, str]]:
    """Return public delivery-serviceability rows for pincode(s) in a query."""
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        return []
    path = Path(configured).expanduser().resolve() / "data" / "pincodes.csv"
    if not path.is_file():
        return []
    codes = {"".join(str(unicodedata.digit(ch)) for ch in match) for match in re.findall(r"(?<!\d)\d{6}(?!\d)", query)}
    if not codes:
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle) if row.get("pincode") in codes]

def calendar_context() -> str:
    """Return the dataset's fixed reference date and supplied holiday calendar."""
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        return "Dataset reference date: 20 October 2026. Business days are Monday–Saturday, excluding dataset holidays; return windows use calendar days."
    path = Path(configured).expanduser().resolve() / "data" / "holidays.csv"
    holidays = []
    if path.is_file():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            holidays = [f"{row.get('date', '')}: {row.get('name', '')}" for row in csv.DictReader(handle)]
    holiday_text = "; ".join(holidays) if holidays else "use the supplied holiday calendar when available"
    return f"Dataset reference date: 20 October 2026. Business days are Monday–Saturday, excluding Sundays and these holidays: {holiday_text}. Return windows use calendar days."
