import csv
from src.catalog import search_products

def test_catalog_exact_sku_lookup(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    with (data / "products.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sku", "title", "brand", "price_inr", "warranty_months", "description"])
        writer.writeheader()
        writer.writerow({"sku":"ELE-0001","title":"Nimbus Wireless Earbuds","brand":"Nimbus","price_inr":"2199","warranty_months":"12","description":"Wireless earbuds"})
        writer.writerow({"sku":"HOM-0002","title":"Steel Water Bottle","brand":"Home","price_inr":"499","warranty_months":"0","description":"Bottle"})
    monkeypatch.setenv("ZENTOMART_DATA_DIR", str(tmp_path))
    found = search_products("warranty for ELE-0001")
    assert found and found[0]["sku"] == "ELE-0001"
    assert found[0]["warranty_months"] == "12"
