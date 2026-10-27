# ZentroMart Voice Agent

An AI-powered customer-support assistant for the fictional ZentroMart store, built for the VoiceOps 2026 capstone.

> **Current status:** Initial text prototype scaffold committed. Retrieval and Gemini response code are implemented, but they have **not been executed or validated in this GitHub-only session**. Order tools, full dataset validation, practice-set evaluation, and Gnani voice flow remain to be integrated and tested.

## Capstone goals

- Answer customer questions using ZentroMart's company documents.
- Retrieve relevant policy/FAQ passages (RAG) and report the source sections used.
- Maintain conversation context for follow-up questions.
- Integrate the supplied `lookup_order(order_id)` and `create_ticket(summary)` tools, including caller verification and honest handoff reporting.
- Use **Gnani.ai only** for speech-to-text (STT) and text-to-speech (TTS).
- Provide a reproducible batch-run command that processes a folder of audio files and saves replies, speech, and retrieved evidence.

## Architecture

```text
Customer text
    ↓
Lexical retrieval over kb/*.md
    ↓
Retrieved excerpts + recent conversation
    ↓
Gemini LLM (GEMINI_API_KEY)
    ↓
Answer + source section IDs

Voice pipeline (planned):
Audio → Gnani STT → same support agent → Gnani TTS → saved reply audio
```

The current retrieval baseline uses lexical scoring rather than vector embeddings. This is an intentionally simple baseline; it must be evaluated against the provided `gold_evidence` labels before claiming retrieval quality. A later iteration can add embeddings if that improves measured results.

## Repository layout

```text
.
├── src/
│   ├── __init__.py
│   ├── agent.py            # Gemini-backed response logic
│   └── retrieval.py        # Markdown chunking and lexical retrieval
├── tests/
│   └── test_retrieval.py
├── data/
│   └── knowledge_base/     # Place permitted kb/*.md files here locally
├── docs/                   # Report and demo notes (to be added)
├── .env.example            # Variable names only; no credentials
├── .gitignore
├── requirements.txt
└── run.py                  # Text-mode prototype entry point
```

## Setup

Python 3.11 or a compatible version is recommended.

1. Clone this repository and open its folder.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   # source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to a local file named `.env`, then add your own `GEMINI_API_KEY` and `GNANI_API_KEY`. Do not commit `.env`.
5. Extract the supplied capstone ZIP locally. Read `README.md`, `DATA_DICTIONARY.md`, and `ZIP_SCHEMA.md` first. Keep the dataset ZIP, customer/order CSVs, and private evaluation data out of this public repository.
6. For the current text prototype, place the supplied `kb/` folder at `data/knowledge_base/` locally, or pass its path to `--kb-dir`.

Run the text prototype:

```bash
python run.py --kb-dir data/knowledge_base
```

Run the retrieval tests:

```bash
pytest -q
```

The text prototype requires a valid Gemini API key. Gnani voice integration is not yet wired into the runnable entry point.

## Dataset rules

- Use the supplied synthetic dataset only; do not use real customer data or real call recordings.
- Keep all customer/order identifiers and pincodes as strings.
- Use the current policy documents and respect their precedence. Superseded policies must not override current policy.
- Historical support logs are context, not policy authority.
- The dataset's reference date is **20 October 2026**. Business-day calculations run Monday–Saturday, excluding dates in `holidays.csv`; return windows use calendar days.
- Verify callers using the supplied tool's required phone-last-four-digits or delivery-pincode check before revealing order details.
- Report ticket creation/handoff only when the tool confirms success.

## Planned milestones

- [x] Create repository scaffold and secret/data exclusions.
- [x] Add Markdown knowledge-base chunking and lexical retrieval baseline.
- [x] Add a Gemini-backed text response prototype with source reporting.
- [ ] Run the code and tests locally; fix any environment or API issues.
- [ ] Inspect the supplied dataset and use the provided validation script.
- [ ] Connect the supplied order lookup and ticket creation tools safely.
- [ ] Add session-aware follow-ups, clarifying questions, refusals, and handoff logic.
- [ ] Evaluate prompt-only (Step 1) versus retrieval-grounded (Step 2) answers on the practice set.
- [ ] Integrate Gnani STT/TTS using the official SDK and named TTS model.
- [ ] Add the required batch audio command and save transcript, response text/audio, and retrieved evidence.
- [ ] Prepare a report of up to four pages and a demo of up to two minutes.

## Security

- Never commit API keys, passwords, access tokens, or a real `.env` file.
- Do not upload the supplied dataset ZIP, raw CSV tables, or private evaluation files.
- Do not add a public license until redistribution rights for all included material are confirmed.
