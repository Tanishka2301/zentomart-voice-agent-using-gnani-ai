from src.agent import extract_order_id, normalize_digits, language_mode

def test_spaced_order_id_is_normalized():
    assert extract_order_id("Order number hai 8978 2837.") == "89782837"

def test_devanagari_order_id_and_verification_digits():
    assert extract_order_id("ऑर्डर नंबर है ७९३६ ३५५०।") == "79363550"
    assert normalize_digits("०७८३") == "0783"

def test_language_detection_for_hindi_and_hinglish():
    assert language_mode("ऑर्डर नंबर है ७९३६ ३५५०") == "hi"
    assert language_mode("Mera refund kahan hai?") == "hi-en"
