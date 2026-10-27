from src.agent import extract_order_id, normalize_digits

def test_spaced_order_id_is_normalized():
    assert extract_order_id("Order number hai 8978 2837.") == "89782837"

def test_devanagari_order_id_and_verification_digits():
    assert extract_order_id("ऑर्डर नंबर है ७९३६ ३५५०।") == "79363550"
    assert normalize_digits("०७८३") == "0783"
