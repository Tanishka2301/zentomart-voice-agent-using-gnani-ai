# ZentroMart Voice Agent

An AI-powered customer-support assistant for the fictional ZentroMart store. This repository will contain the application code, setup instructions, and evaluation/demo materials for the VoiceOps capstone.

> **Project status:** Initial repository scaffold. Features listed below are planned until implemented and tested.

## Goals

- Answer customer questions using a large language model (LLM).
- Retrieve grounded answers from ZentroMart's knowledge base using retrieval-augmented generation (RAG).
- Maintain conversational context during a session.
- Provide mock order lookup and support-ticket tools using safe sample data.
- Escalate unresolved or sensitive cases to a human-support workflow.
- Integrate Gnani.ai speech-to-text (STT) and text-to-speech (TTS), subject to available API credentials and documentation.

## Planned request flow

1. Receive a typed or spoken customer query.
2. If speech is used, convert speech to text through the speech provider.
3. Retrieve relevant knowledge-base passages.
4. Send the query, retrieved context, and conversation history to the configured LLM.
5. Invoke an approved mock tool when an order lookup or support ticket is needed.
6. Return the answer as text and, when configured, synthesized speech.
7. Escalate when the assistant cannot safely or confidently resolve the issue.

## Repository layout

```text
zentomart-voice-agent-using-gnani-ai/
├── app/                 # Application modules (to be added)
├── data/
│   └── knowledge_base/  # Sanitized, permitted knowledge-base documents only
├── tests/               # Automated tests
├── docs/                # Architecture, report, and demo notes
├── .env.example         # Names of required environment variables; no secrets
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Python 3.11 or a compatible supported version is recommended.

1. Install Python and Git.
2. Clone this repository.
3. Create and activate a virtual environment.
4. Install dependencies from `requirements.txt`.
5. Copy `.env.example` to `.env` and fill in your own API credentials locally.
6. Follow the run instructions that will be added when the application entry point is implemented.

The exact provider SDKs, model, and run command will be documented after the implementation is selected and tested.

## Configuration and security

- Never commit API keys, passwords, access tokens, or a real `.env` file.
- Do not upload the supplied capstone dataset ZIP, customer/order records, or private evaluation data.
- Use only sanitized and permitted knowledge-base content in the public repository.
- Keep mock order/ticket data synthetic and clearly labelled as test data.
- Validate tool inputs and avoid exposing one customer's data to another session.

## Planned milestones

- [ ] Inspect the brief and dataset structure locally; identify files safe to use.
- [ ] Build the minimal customer-support chat flow.
- [ ] Add knowledge-base retrieval (RAG).
- [ ] Add session memory and mock order/ticket tools.
- [ ] Add human handoff behavior.
- [ ] Integrate Gnani.ai STT/TTS where credentials and API access permit.
- [ ] Add tests and a reproducible batch-run command.
- [ ] Prepare a report (maximum 4 pages) and a demo (maximum 2 minutes).

## Deliverables

- Source code and setup/run instructions.
- A reproducible batch-run command.
- A report of up to four pages.
- A demo video of up to two minutes.

## License and dataset

Only add a license after confirming that the source code and any included materials may be redistributed. The capstone dataset and customer/order records are intentionally excluded from this repository.
