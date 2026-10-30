# Final Submission Checklist

This checklist records the evidence currently available for the ZentroMart VoiceOps 2026 capstone. Do not mark unverified provider or demo steps as complete.

## Verified repository state

- [x] Project source, setup instructions, evaluation scripts, voice batch pipeline and documentation are present.
- [x] .env.example uses placeholders; keep the real .env private and uncommitted.
- [x] Dataset import produced 21 Markdown knowledge-base files in the local Codespaces workspace.
- [x] GitHub Actions test workflow passed on the latest checked run (41023942202).
- [x] A previous local test run reported 34 passed, 1 skipped. This is historical evidence, not a fresh run.
- [x] Gemini connectivity smoke test returned API_OK.

## Evaluation evidence currently available

A separate one-question smoke evaluation reported: 1/1 evaluated; RAG evidence hit rate 100%; prompt-only had 1 row missing required facts; RAG had 0; forbidden-claim matches were 0.

The later limited evaluation reported: 2/5 questions evaluated; 3 rows did not complete; RAG evidence hit rate 100% across the 2 evaluated rows; prompt-only had 2 evaluated rows missing required facts; RAG had 0; forbidden-claim matches were 0.

These are small, partial diagnostic samples—not a full benchmark or proof of general accuracy. The three incomplete rows' error details have not been reviewed. The evaluation JSON is local and ignored by Git.

## Not yet verified — disclose honestly

- [ ] Full 52-question evaluation.
- [ ] Full 23-conversation / 96-turn evaluation.
- [ ] Successful end-to-end Gnani STT → agent → Gnani TTS run with a self-recorded clip.
- [ ] Final live demo recording.
- [ ] Final report with complete measured test, evaluation, conversation and voice results.

Gemini free-tier quota/service errors were encountered. Do not repeatedly rerun generation or describe incomplete runs as successful.

## Final demo and safety

- Use only supplied synthetic order data and self-recorded audio.
- Demonstrate that order details remain hidden until the mock verification tool succeeds.
- Claim ticket creation only when the mock tool returns created=True.
- State clearly that order verification and ticketing are educational mocks, not production authentication or a live ticketing service.
- Never commit API keys, .env, raw customer/order CSVs, practice labels, generated ticket files or private recordings.

**Submission guidance:** The repository and CI are in place, and a small RAG evaluation sample is encouraging. Submit with the limitations above clearly stated; do not claim full evaluation or end-to-end voice validation.