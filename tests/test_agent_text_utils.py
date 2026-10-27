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


def test_order_question_is_redacted_from_history_until_verification(monkeypatch):
    from src import agent as agent_module

    monkeypatch.setattr(
        agent_module, "lookup_order",
        lambda order_id, verification_value=None: {
            "found": True, "verified": False, "verification_required": True
        },
    )
    # Avoid constructing a Gemini client; exercise only the local guardrails.
    agent = object.__new__(agent_module.SupportAgent)
    agent.history = []
    agent.order_id = None
    agent.verified_order = None
    agent.verification_attempts = 0
    agent.awaiting_verification = False
    agent.introduced = False
    agent.pending_question = None

    result = agent.respond("Please check order 1234-5678")

    assert result["tool_calls"] == [{"tool": "lookup_order", "verified": False}]
    assert agent.awaiting_verification is True
    assert agent.order_id == "12345678"
    assert "12345678" not in str(agent.history)
    assert "[ORDER_ID]" in str(agent.history)
    assert agent.pending_question is not None
    assert "12345678" not in agent.pending_question


def test_verification_digits_are_not_added_to_history(monkeypatch):
    from src import agent as agent_module

    monkeypatch.setattr(
        agent_module, "lookup_order",
        lambda order_id, verification_value=None: {
            "found": False, "verified": False, "verification_required": True
        },
    )
    agent = object.__new__(agent_module.SupportAgent)
    agent.history = []
    agent.order_id = "12345678"
    agent.verified_order = None
    agent.verification_attempts = 0
    agent.awaiting_verification = True
    agent.introduced = True
    agent.pending_question = "Where is order [ORDER_ID]?"

    result = agent.respond("My registered phone ends in 4321")

    assert result["tool_calls"][-1]["verified"] is False
    assert "4321" not in str(agent.history)
    assert agent.verification_attempts == 1
