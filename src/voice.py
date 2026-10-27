"""Gnani.ai speech adapter for the ZentroMart support agent.

Gnani is the only permitted STT/TTS provider for this capstone. This module
follows the SDK calls documented in the supplied VoiceOps brief.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient

from src.agent import SupportAgent


def transcribe_audio(audio_path: str | Path, language_code: str = "en-IN") -> str:
    """Transcribe one audio file using Gnani STT."""
    if not os.getenv("GNANI_API_KEY", "").strip():
        raise RuntimeError("GNANI_API_KEY is missing from the local environment.")
    client = GnaniSTTClient()
    result = client.transcribe(str(audio_path), language_code=language_code)
    transcript = str(result.get("transcript", "")).strip()
    return transcript


def process_voice_turn(
    audio_path: str | Path,
    agent: SupportAgent,
    output_audio_path: str | Path,
    language_code: str = "en-IN",
    voice: str = "Kaveri",
    tts_model: str = "timbre-v2.5",
) -> dict[str, Any]:
    """Transcribe, answer, synthesize, and return auditable turn metadata."""
    heard = transcribe_audio(audio_path, language_code=language_code)
    if not heard:
        answer = "Sorry, I didn't catch that. Could you say that again?"
        sources: list[dict[str, Any]] = []
    else:
        result = agent.respond(heard)
        answer = result["answer"]
        sources = result["sources"]

    if not os.getenv("GNANI_API_KEY", "").strip():
        raise RuntimeError("GNANI_API_KEY is missing from the local environment.")
    output_path = Path(output_audio_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tts = GnaniTTSClient()
    tts.synthesize(
        answer,
        voice=voice,
        model=tts_model,
        language=language_code,
        output_file=str(output_path),
    )
    return {
        "input_audio": str(audio_path),
        "transcript": heard,
        "answer": answer,
        "output_audio": str(output_path),
        "sources": sources,
    }
