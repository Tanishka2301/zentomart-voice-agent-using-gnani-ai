# ZentroMart Voice Agent

An AI customer-support assistant for the fictional ZentroMart store, built for the VoiceOps 2026 capstone.

> **Implementation status:** Dataset-aware retrieval, Gemini response generation, identity-gated order lookup, synthetic escalation tickets, practice-question evaluation, and a Gnani STT/TTS batch pipeline are implemented in the repository. They still require execution with your local API credentials and the supplied dataset; do not treat them as validated until the tests and end-to-end run pass.

## Features

- Retrieval over the supplied Markdown knowledge base, preserving section IDs and excluding superseded documents.
- Policy-aware ranking: current policy documents rank above agent guides, help articles, FAQs and marketing pages.
- Gemini-backed concise responses with source/evidence reporting and recent-turn context.
- Order lookup through the dataset's original `tools/tools.py`. Order details are not returned until the caller supplies the registered phone's last four digits or delivery pincode.
- Synthetic human-handover tickets through the supplied `create_ticket` tool. The agent reports a ticket only when the tool confirms creation.
- Gnani.ai STT/TTS adapter and batch audio processing; no audio files are included in the dataset.
- Practice-question evaluation output with required/forbidden fact checks and evidence-hit tracking.

## Setup

Python 3.11 or compatible is recommended.

1. Clone this repository and open the project folder.
2. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux
   # source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Extract the supplied `Capstone_Project_Dataset_FTTT_2026.zip` outside this repository. Keep the ZIP, raw CSVs, practice labels, customer/order records and generated ticket file out of GitHub.
4. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`, `GNANI_API_KEY`, and `ZENTOMART_DATA_DIR` to your local values. Set `ZENTOMART_DATA_DIR` to the absolute path of the extracted folder containing `tools/`, `data/`, `kb/`, and `practice/`. Never commit `.env` or keys.
5. Copy the KB documents into the local project:

   ```bash
   python scripts/import_dataset.py "PATH/TO/Capstone_Project_Dataset_FTTT_2026"
   ```

   Replace the example path with your extracted dataset folder. This copies only Markdown KB files into `data/knowledge_base/`; it does not copy the CSVs or evaluation labels.

6. Run the supplied dataset validator from the extracted dataset folder:

   ```bash
   python validate_dataset.py
   ```

## Run

Text mode:

```bash
python run.py --kb-dir data/knowledge_base
```

Tests:

```bash
pytest -q
```

Evaluate the 52 single-turn practice questions (requires Gemini access):

```bash
python scripts/evaluate.py --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --kb-dir data/knowledge_base
```

Use `--limit 5` for a quick smoke run. The JSON report is written to `outputs/evaluation.json`, which is ignored by Git.

Evaluate the 23 multi-turn practice conversations, including expected tool-call checks:

```bash
python scripts/evaluate_conversations.py --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --kb-dir data/knowledge_base
```

This creates `outputs/conversation_evaluation.json`. Review flagged turns manually; automated fact matching is a diagnostic, not a substitute for human review.

Batch voice processing (record your own audio; the dataset has no prerecorded audio):

```bash
python run_audio.py --input-dir recordings --output-dir outputs/voice --kb-dir data/knowledge_base --language en-IN
```

Supported input extensions are WAV, MP3, FLAC, OGG and M4A. Gnani SDK behavior and audio formats must be smoke-tested with your account.

## Dataset and safety rules

- All supplied customer/order data is synthetic. Do not use real customer information or real call recordings.
- Keep identifiers such as order IDs, customer IDs, SKUs, pincodes and refund references as strings.
- The fixed dataset reference date is **20 October 2026**. Business days are Monday–Saturday excluding dates in `holidays.csv`; return windows use calendar days.
- Current policy documents take precedence over agent guides, help articles, FAQs and marketing. Superseded policy documents are excluded from retrieval.
- Historical support logs are examples of past human behavior, not policy authority.
- Verify callers before disclosing specific order status, items, addresses, amounts or refund information. The supplied verification mechanism is a synthetic educational mock, not production-grade authentication.
- Never include API keys, `.env`, raw data, practice labels or generated tickets in a public repository.
- No license is added because redistribution rights for the supplied capstone material have not been established.

## Project structure

```text
src/
  agent.py             # Gemini response flow, verification gate, ticket escalation
  business_tools.py    # safe adapter to the supplied offline tools
  retrieval.py         # metadata-aware Markdown chunking and retrieval
  voice.py             # Gnani STT/TTS adapter
scripts/
  import_dataset.py    # copies KB Markdown only
  evaluate.py          # practice-question checks and evidence tracking
tests/
run.py                  # text chat
run_audio.py            # batch audio pipeline
```
