"""Batch-process audio files through Gnani STT, the agent, and Gnani TTS."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.agent import SupportAgent
from src.retrieval import KnowledgeBase
from src.voice import process_voice_turn

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process a folder of audio files and save text, speech, and evidence."
    )
    parser.add_argument("--input-dir", required=True, help="Folder containing customer audio files")
    parser.add_argument("--output-dir", default="outputs", help="Folder for JSON, TXT, and WAV replies")
    parser.add_argument("--kb-dir", default="data/knowledge_base", help="Folder containing kb Markdown files")
    parser.add_argument("--language", default="en-IN", help="Gnani STT language code, e.g. en-IN or hi-IN")
    parser.add_argument("--tts-language", default="auto", help="Gnani TTS language: auto, en-IN, hi-IN, or hi-en")
    parser.add_argument("--voice", default="Kaveri", help="Gnani TTS voice")
    parser.add_argument("--tts-model", default="timbre-v2.5", help="Gnani TTS model")
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("GNANI_API_KEY", "").strip():
        parser.error("GNANI_API_KEY is missing; add it to your local .env file.")
    if not os.getenv("GEMINI_API_KEY", "").strip():
        parser.error("GEMINI_API_KEY is missing; add it to your local .env file.")

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        parser.error(f"Input directory does not exist: {input_dir}")

    files = sorted(path for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS)
    if not files:
        parser.error(f"No supported audio files found in {input_dir}")

    kb = KnowledgeBase.from_directory(args.kb_dir)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    agent = SupportAgent(kb)
    manifest = []

    for audio_path in files:
        relative = audio_path.relative_to(input_dir)
        target_dir = output_root / relative.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        stem = relative.stem
        reply_audio = target_dir / f"{stem}_reply.wav"
        result_json = target_dir / f"{stem}_result.json"
        result_text = target_dir / f"{stem}_reply.txt"

        # Each file is a separate customer session. Reset all state, especially
        # order-verification state, so one caller can never inherit another's session.
        agent.reset()
        try:
            result = process_voice_turn(
                audio_path=audio_path,
                agent=agent,
                output_audio_path=reply_audio,
                language_code=args.language,
                tts_language=args.tts_language,
                voice=args.voice,
                tts_model=args.tts_model,
            )
            result_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result_text.write_text(
                f"Transcript:\n{result['transcript']}\n\nReply:\n{result['answer']}\n",
                encoding="utf-8",
            )
            manifest.append({"input_audio": str(audio_path), "status": "ok", "result_json": str(result_json)})
            print(f"[OK] {audio_path} -> {reply_audio}")
        except Exception as exc:
            failure = {
                "input_audio": str(audio_path),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            result_json.write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8")
            manifest.append({"input_audio": str(audio_path), "status": "error", "error": str(exc)})
            print(f"[ERROR] {audio_path}: {exc}")

    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    succeeded = sum(item["status"] == "ok" for item in manifest)
    print(f"Finished: {succeeded}/{len(manifest)} audio files processed. See {output_root}.")
    return 0 if succeeded == len(manifest) else 1


if __name__ == "__main__":
    raise SystemExit(main())
