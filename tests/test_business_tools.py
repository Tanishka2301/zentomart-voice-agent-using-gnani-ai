import pytest
from src.business_tools import lookup_order

def test_lookup_requires_dataset_configuration(monkeypatch):
    monkeypatch.delenv("ZENTOMART_DATA_DIR", raising=False)
    with pytest.raises(RuntimeError, match="ZENTOMART_DATA_DIR"):
        lookup_order("12345678")
