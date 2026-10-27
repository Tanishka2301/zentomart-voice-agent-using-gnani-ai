"""Offline tests for voice-turn orchestration; no Gnani API calls are made."""
from __future__ import annotations

import importlib
import sys
import types


def _load_voice_module(monkeypatch):
    gnani = types.ModuleType("gnani")
    stt = types.ModuleType("gnani.stt")
    tts = types.ModuleType("gnani.tts")

    class DummySTT:
        pass

    class DummyTTS:
        pass

    stt.GnaniSTTClient = DummySTT
    tts.GnaniTTSClient = DummyTTS
    gnani.stt = stt
    gnani.tts = tts
    monkeypatch.setitem(sys.modules, "gnani", gnani)
    monkeypatch.setitem(sys.modules, "gnani.stt", stt)
    monkeypatch.setitem(sys.modules, "gnani.tts", tts)
    sys.modules.pop("src.voice", None)
    return importlib.import_module("src.voice")


def test_process_voice_turn_synthesizes_answer_and_returns_sources(tmp_path, monkeypatch):
    voice = _load_voice_module(monkeypatch)
    monkeypatch.setenv("GNANI_API_KEY", "test-key")
    monkeypatch.setattr(voice, "transcribe_audio", lambda *args, **kwargs: "Where is my order?")

    class Agent:
        def respond(self, text):
            assert text == "Where is my order?"
            return {"answer": "Your order is being processed.", "sources": [{"section_id": "ORD-1"}]}

    calls = {}

    class FakeTTS:
        def synthesize(self, text, **kwargs):
            calls["text"] = text
            calls.update(kwargs)
            Path(kwargs["output_file"]).write_bytes(b"fake audio")

    from pathlib import Path
    monkeypatch.setattr(voice, "GnaniTTSClient", FakeTTS)

    target = tmp_path / "reply.wav"
    result = voice.process_voice_turn("input.wav", Agent(), target)

    assert result["transcript"] == "Where is my order?"
    assert result["answer"] == "Your order is being processed."
    assert result["sources"] == [{"section_id": "ORD-1"}]
    assert result["tts_language"] == "en-IN"
    assert target.read_bytes() == b"fake audio"
    assert calls["text"] == result["answer"]


def test_empty_transcript_uses_retry_prompt_without_agent_call(tmp_path, monkeypatch):
    voice = _load_voice_module(monkeypatch)
    monkeypatch.setenv("GNANI_API_KEY", "test-key")
    monkeypatch.setattr(voice, "transcribe_audio", lambda *args, **kwargs: "")

    class Agent:
        def respond(self, text):
            raise AssertionError("Agent must not be called for empty transcription")

    class FakeTTS:
        def synthesize(self, text, **kwargs):
            self.text = text

    monkeypatch.setattr(voice, "GnaniTTSClient", FakeTTS)
    result = voice.process_voice_turn("input.wav", Agent(), tmp_path / "reply.wav")

    assert result["transcript"] == ""
    assert result["sources"] == []
    assert "say that again" in result["answer"].lower()
