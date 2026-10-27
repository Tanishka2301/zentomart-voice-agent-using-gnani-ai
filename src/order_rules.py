"""Deterministic date and refund-escalation rules for the frozen capstone dataset."""
from __future__ import annotations
import csv
import os
from datetime import date, timedelta
from pathlib import Path

REFERENCE_DATE = date(2026, 10, 20)
MAX_BUSINESS_DAYS = {
    "upi": 3,
    "card": 7,
    "netbanking": 5,
    "wallet": 0,
    "cod_bank": 7,
    "cod_wallet": 0,
}

def load_holidays() -> set[date]:
    fallback = {
        date(2026, 8, 15), date(2026, 10, 2),
        date(2026, 10, 19), date(2026, 11, 9),
    }
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        return fallback
    path = Path(configured).expanduser().resolve() / "data" / "holidays.csv"
    if not path.is_file():
        return fallback
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {date.fromisoformat(row["date"]) for row in csv.DictReader(handle) if row.get("date")}

def add_business_days(start: date, count: int, holidays: set[date]) -> date:
    """Add business days after start; Sundays and supplied holidays do not count."""
    current = start
    added = 0
    while added < count:
        current += timedelta(days=1)
        if current.weekday() != 6 and current not in holidays:
            added += 1
    return current

def business_days_after(start: date, end: date, holidays: set[date]) -> int:
    """Count business days strictly after start and up to and including end."""
    if end <= start:
        return 0
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() != 6 and current not in holidays:
            count += 1
        current += timedelta(days=1)
    return count

def refund_overdue(order: dict, question: str) -> dict | None:
    """Return evidence for an overdue, reportedly missing refund; otherwise None."""
    low = question.casefold()
    complaint = any(term in low for term in (
        "refund not received", "refund hasn't arrived", "refund has not arrived",
        "refund hasn't come", "refund has not come", "refund is late", "refund delayed",
        "where is my refund", "where's my refund", "still no refund",
        "money not credited", "money hasn't arrived", "money has not arrived",
        "still waiting for refund", "refund not credited", "not credited yet",
        "haven't received my refund", "have not received my refund",
    ))
    if not complaint:
        return None
    candidates = []
    for prefix in ("return", "cancellation", "rto"):
        initiated = str(order.get(f"{prefix}_refund_initiated_on") or "").strip()
        method = str(order.get(f"{prefix}_refund_method") or "").strip().lower()
        if not initiated or method not in MAX_BUSINESS_DAYS:
            continue
        if prefix == "return" and order.get("return_refund_completed_on"):
            continue
        try:
            started = date.fromisoformat(initiated[:10])
        except ValueError:
            continue
        candidates.append((started, prefix, method))
    if not candidates:
        return None
    started, prefix, method = max(candidates)
    holidays = load_holidays()
    due = add_business_days(started, MAX_BUSINESS_DAYS[method], holidays)
    overdue_days = business_days_after(due, REFERENCE_DATE, holidays)
    if overdue_days > 3:
        return {
            "reason": "refund_more_than_3_business_days_past_maximum_timeline",
            "refund_type": prefix,
            "initiated_on": started.isoformat(),
            "payment_method": method,
            "maximum_timeline_business_days": MAX_BUSINESS_DAYS[method],
            "maximum_due_date": due.isoformat(),
            "business_days_past_maximum": overdue_days,
        }
    return None
