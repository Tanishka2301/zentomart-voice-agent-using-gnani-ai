# VoiceOps 2026 — ZentroMart Support Agent Report (Draft)

> **Before submission:** Replace every `[FILL AFTER RUN]` field with measured results from the actual local run. Do not claim end-to-end voice success until a Gnani STT → agent → Gnani TTS test has completed successfully. Keep the final report within four pages.

## 1. Problem and objective

ZentroMart support questions cover delivery, cancellation, returns, refunds, product warranty, payment and escalation. The objective is to build a concise support assistant that grounds answers in current company documents, uses the supplied synthetic data tools for order-specific requests, maintains multi-turn context, and supports voice input/output using Gnani.ai.

## 2. System design

**Text/RAG flow:** Customer message → Markdown section retrieval → product/pincode/calendar context when relevant → Gemini response → answer plus source-section IDs.

**Order-specific flow:** Ask for order ID → request either registered-phone last four digits or the order delivery pincode → call the supplied identity-gated lookup → disclose order details only after successful verification. Allow one retry; do not store the verification value in conversation history or ticket summaries.

**Escalation flow:** Identify safety/fraud/legal/human requests, high-value damaged items, repeated contacts, compensation/exception requests, or sufficiently overdue reported refunds → call the supplied ticket tool → confirm handoff only when the tool returns `created=True`.

**Voice flow:** Audio file → Gnani STT → same support agent → Gnani TTS → save transcript, reply text, reply audio and retrieved evidence.

## 3. Retrieval and data handling

The retrieval baseline uses lexical scoring over Markdown sections while retaining section IDs. Superseded documents are excluded and current policy documents receive higher ranking than agent guides, help pages, FAQs and marketing pages. Product records and pincode serviceability are read from the supplied CSVs. The fixed dataset reference date is 20 October 2026; business days exclude Sundays and supplied holidays, while return windows use calendar days.

All supplied records are synthetic. The raw ZIP, customer/order CSVs, practice labels, API keys, local `.env`, and generated ticket file must remain outside the public repository.

## 4. Evaluation

Run the supplied dataset validator, automated tests, question evaluator and multi-turn conversation evaluator before submission.

| Measurement | Result |
|---|---|
| Dataset validator | [FILL AFTER RUN] |
| Unit/security tests | [FILL AFTER RUN] |
| Practice questions evaluated | [FILL AFTER RUN] / 52 |
| Prompt-only rows missing required facts | [FILL AFTER RUN] |
| RAG rows missing required facts | [FILL AFTER RUN] |
| RAG evidence hit rate | [FILL AFTER RUN] |
| Conversation turns evaluated | [FILL AFTER RUN] / 96 |
| Voice files processed successfully | [FILL AFTER RUN] / [TOTAL TEST FILES] |

**What improved from prompt-only to RAG:** [FILL AFTER RUN using `outputs/evaluation.json` and observed examples.]

**Failure cases and next improvements:** [FILL AFTER RUN. Include retrieval misses, ambiguous questions, tool-call mismatches, ASR errors, latency, and any provider/API errors actually observed.]

## 5. Limitations and conclusion

Lexical retrieval may miss paraphrases or semantically related policy passages. Automated substring-based rubric checks are diagnostic and require manual review. The supplied identity verification and ticket tools are educational mocks, not production authentication or a live ticketing service. Voice integration must be validated using the configured Gnani account and representative recordings.

The project combines policy-grounded response generation, stateful order verification, tool-backed escalation, and a batch voice interface. Final claims should be limited to features and measurements verified in the completed run.
