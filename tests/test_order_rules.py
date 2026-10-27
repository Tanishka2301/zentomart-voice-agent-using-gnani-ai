from datetime import date
import csv
from src.order_rules import add_business_days, business_days_after, refund_overdue

def test_business_day_count_skips_sunday_and_holidays():
    holidays = {date(2026, 10, 19)}
    assert add_business_days(date(2026, 10, 16), 2, holidays) == date(2026, 10, 20)
    assert business_days_after(date(2026, 10, 16), date(2026, 10, 20), holidays) == 2

def test_refund_escalation_requires_customer_report_and_overdue_timeline(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    with (data / "holidays.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "name"])
        writer.writeheader()
        writer.writerow({"date": "2026-10-19", "name": "Warehouse closure"})
    monkeypatch.setenv("ZENTOMART_DATA_DIR", str(tmp_path))
    order = {
        "return_refund_initiated_on": "2026-10-01",
        "return_refund_method": "card",
        "return_refund_completed_on": "",
        "cancellation_refund_initiated_on": "",
        "rto_refund_initiated_on": "",
    }
    assert refund_overdue(order, "My refund not received")["business_days_past_maximum"] > 3
    assert refund_overdue(order, "What is the refund policy?") is None

def test_completed_return_refund_is_not_marked_overdue(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    (data / "holidays.csv").write_text("date,name\n", encoding="utf-8")
    monkeypatch.setenv("ZENTOMART_DATA_DIR", str(tmp_path))
    order = {
        "return_refund_initiated_on": "2026-09-01",
        "return_refund_method": "card",
        "return_refund_completed_on": "2026-09-10",
        "cancellation_refund_initiated_on": "",
        "rto_refund_initiated_on": "",
    }
    assert refund_overdue(order, "My refund not received") is None
