# Two-minute demo script

> Record only after the local run works. Use synthetic dataset scenarios and do not show API keys or the raw CSV files.

- **0:00–0:15 — Introduce the system.** “This is the ZentroMart AI support assistant. It answers from current company documents and shows which sections support the answer.”
- **0:15–0:40 — Grounded policy question.** Ask a policy question from the supplied practice set. Show the short answer and the retrieved section IDs.
- **0:40–1:05 — Multi-turn order flow.** Give a synthetic order ID in the format shown in the practice conversations. Show that the assistant asks for either the registered phone’s last four digits or delivery pincode before revealing any order details. Use the matching synthetic verification value from the local practice dataset.
- **1:05–1:30 — Follow-up or handoff.** Ask a follow-up about the same order. If using the handoff scenario, ask for a human or use a policy-required escalation. Show the ticket confirmation only if the mock tool actually returned `created=True`.
- **1:30–1:50 — Voice.** Play a short self-recorded test clip, show the Gnani transcript, answer text, output audio and evidence metadata.
- **1:50–2:00 — Close.** State one measured result from the evaluation JSON and one limitation you observed.

Do not fake a successful tool call, voice response, or evaluation score. If any stage fails, fix it before recording the final demo.
