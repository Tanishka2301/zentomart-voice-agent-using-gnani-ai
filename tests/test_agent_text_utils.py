from src.agent import extract_order_id, language_mode, normalize_digits, verification_prompt


def test_extract_order_id_normalizes_separated_digits():
    assert extract_order_id("My order number is 1234-5678") == "12345678"
    assert extract_order_id("Order 12345678 is delayed") == "12345678"


def test_extract_order_id_does_not_accept_short_number():
    assert extract_order_id("My order number is 5678") is None


def test_normalize_digits_handles_devanagari_numerals():
    assert normalize_digits("१२३४") == "1234"


def test_language_mode_detects_hindi_and_hinglish():
    assert language_mode("मेरा ऑर्डर कहाँ है?") == "hi"
    assert language_mode("Mera order kahan hai?") == "hi-en"
    assert language_mode("Where is my order?") == "en"


def test_verification_prompt_matches_language():
    assert "registered phone number" in verification_prompt("en")
    assert "last 4 digits" in verification_prompt("hi-en")
    assert "आख़िरी चार अंक" in verification_prompt("hi")
