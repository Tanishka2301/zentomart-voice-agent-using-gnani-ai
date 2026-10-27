"""Security checks for the supplied synthetic dataset tools.

Set ZENTOMART_DATA_DIR to the extracted dataset root to enable these tests.
No real customer data should ever be used.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import pytest

from src.business_tools import lookup_order


@pytest.fixture
def dataset_root() -> Path:
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        pytest.skip("ZENTOMART_DATA_DIR is not set; dataset-backed security test skipped")
    root = Path(configured).expanduser().resolve()
    if not (root / "tools" / "tools.py").is_file():
        pytest.skip("Supplied dataset tools are not present")
    return root


def _first_order_and_customer(root: Path):
    with (root / "data" / "orders.csv").open(encoding="utf-8-sig", newline="") as f:
        order = next(csv.DictReader(f))
    with (root / "data" / "customers.csv").open(encoding="utf-8-sig", newline="") as f:
        customer = next(row for row in csv.DictReader(f) if row["customer_id"] == order["customer_id"])
    return order, customer


def test_order_lookup_never_discloses_details_before_verification(dataset_root, monkeypatch):
    monkeypatch.setenv("ZENTOMART_DATA_DIR", str(dataset_root))
    order, customer = _first_order_and_customer(dataset_root)

    pending = lookup_order(order["order_id"])
    assert pending.get("verification_required") is True
    assert "status" not in pending
    assert "items" not in pending
    assert "customer_first_name" not in pending

    wrong = "0000" if customer["phone"][-4:] != "0000" else "9999"
    denied = lookup_order(order["order_id"], verification_value=wrong)
    assert denied.get("verified") is False
    assert "status" not in denied
    assert "items" not in denied

    verified = lookup_order(order["order_id"], verification_value=customer["phone"][-4:])
    assert verified.get("verified") is True
    assert verified.get("found") is True
    assert "status" in verified
    assert "items" in verified
    assert "phone_last4" not in verified
