from types import SimpleNamespace
from collections import Counter
from src import agent as agent_module
from src.agent import SupportAgent
from src.retrieval import Chunk, KnowledgeBase

class FakeModels:
    def __init__(self):
        self.prompts = []
    def generate_content(self, model, contents):
        self.prompts.append(contents)
        return SimpleNamespace(text="I can help with that verified order.")

class FakeClient:
    def __init__(self):
        self.models = FakeModels()

def make_agent(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    client = FakeClient()
    monkeypatch.setattr(agent_module.genai, "Client", lambda **kwargs: client)
    kb = KnowledgeBase([Chunk("faq.md", "FAQ-1", "Refund policy information", Counter({"refund": 1, "policy": 1}), "faq")])
    return SupportAgent(kb), client

def test_order_details_are_gated_and_verification_secret_is_not_prompted(monkeypatch):
    agent, client = make_agent(monkeypatch)
    calls = []
    def fake_lookup(order_id, verification_value=None):
        calls.append((order_id, verification_value))
        if verification_value is None:
            return {"verification_required": True}
        if verification_value == "4533":
            return {
                "found": True, "verified": True, "order_id": order_id,
                "status": "shipped", "delivery_pincode": "110001",
                "customer_id": "CUST-01", "contacts_last_7_days": 0,
                "items": [], "total_inr": 1000,
            }
        return {"verified": False}
    monkeypatch.setattr(agent_module, "lookup_order", fake_lookup)
    first = agent.respond("Can you check order 1234 5678?")
    assert "verification" in first["answer"].lower()
    assert client.models.prompts == []
    second = agent.respond("My last four digits are 4533")
    assert second["answer"] == "I can help with that verified order."
    prompt = client.models.prompts[-1]
    assert "4533" not in prompt
    assert "110001" not in prompt
    assert "CUST-01" not in prompt
    assert calls == [("12345678", None), ("12345678", "4533")]

def test_two_failed_verification_attempts_never_call_llm(monkeypatch):
    agent, client = make_agent(monkeypatch)
    monkeypatch.setattr(agent_module, "lookup_order", lambda order_id, verification_value=None:
                        {"verification_required": True} if verification_value is None else {"verified": False})
    agent.respond("Order number is 1234 5678")
    first = agent.respond("1111")
    second = agent.respond("2222")
    assert "try once more" in first["answer"].lower()
    assert "share order information" in second["answer"].lower()
    assert client.models.prompts == []
