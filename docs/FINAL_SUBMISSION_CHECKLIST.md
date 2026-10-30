# Final Submission Checklist

Use this checklist before submitting the ZentroMart VoiceOps capstone. Record only results you actually observe.

## 1. Repository and setup

- [ ] Confirm `.env` exists locally and contains working credentials. Never commit it or paste keys into chat.
- [ ] Confirm `ZENTOMART_DATA_DIR` points to the extracted `Capstone_Project_Dataset_FTTT_2026` folder.
- [ ] Confirm the imported knowledge base is present in `data/knowledge_base/`.
- [ ] Run the dataset validator from the extracted dataset directory: `python validate_dataset.py`.
- [ ] Run preflight: `python scripts/preflight.py --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --audio`.

## 2. Automated checks

- [ ] Run `python -m compileall -q src scripts run.py run_audio.py`.
- [ ] Run `python -m pytest -q`.
- [ ] Record the exact pass, skip and failure counts. Explain any skipped tests.

## 3. Gemini and retrieval evaluation

- [ ] Confirm Gemini access with a small text-generation request before running the evaluators.
- [ ] Run a small smoke evaluation first: `python -m scripts.evaluate --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --kb-dir data/knowledge_base --limit 1`.
- [ ] If that succeeds, run the full 52-question evaluation when quota and time permit: `python -m scripts.evaluate --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --kb-dir data/knowledge_base`.
- [ ] Run multi-turn evaluation when ready: `python -m scripts.evaluate_conversations --dataset-dir "PATH/TO/Capstone_Project_Dataset_FTTT_2026" --kb-dir data/knowledge_base`.
- [ ] Review `outputs/evaluation.json` and `outputs/conversation_evaluation.json`; record actual counts, errors, evidence-hit rate and limitations. Do not treat substring-based rubric checks as proof of semantic correctness.
- [ ] If a provider quota or service error occurs, record it as an incomplete evaluation; do not report it as a model or RAG pass.

## 4. Voice smoke test

- [ ] Use a short, self-recorded test clip (no real customer audio).
- [ ] Run the batch voice command from the README with the configured Gnani account.
- [ ] Confirm the transcript, generated answer, output audio and evidence metadata are produced.
- [ ] Record the number of successful and failed clips. Do not claim end-to-end voice success based only on imports or preflight.

## 5. Demo and report

- [ ] Follow `docs/demo_script.md` and show only scenarios that work live.
- [ ] Use synthetic order data and show the verification gate before order details are disclosed.
- [ ] Show a handoff ticket only when the supplied mock tool confirms ticket creation.
- [ ] Replace every `[FILL AFTER RUN]` placeholder in `docs/report_template.md` with measured results, or remove the draft-only template from the submitted report.
- [ ] State clearly that the supplied order verification and ticketing tools are educational mocks, not production authentication or a live ticketing service.
- [ ] Do not include API keys, `.env`, raw customer/order CSVs, practice labels, generated ticket files or private recordings in the public repository.

## Current known status

- GitHub Actions test workflow: passing on the repository's latest checked commit before this checklist was added.
- Local test run previously reported: 34 passed, 1 skipped. Re-run before submission and use the fresh output.
- Gemini practice-question evaluation: previously blocked by a Gemini 429 free-tier quota response; a successful run has not yet been confirmed.
- Complete Gnani STT → agent → TTS batch run: not yet confirmed.
- Final demo recording and completed measured report: not yet confirmed.

**Submission rule:** Mark a checkbox only after you have personally run the corresponding step and saved its actual result.
