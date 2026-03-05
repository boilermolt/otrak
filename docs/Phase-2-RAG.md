# Phase 2 — Agreement RAG + Policy Q&A

## Goal
Provide a safe, cited Q&A chatbot for collective bargaining agreements to help interpret rules and edge cases **without** replacing deterministic allocation logic.

## Why separate from allocation
- Allocation needs deterministic, testable rules
- RAG is probabilistic and should **inform**, not decide
- Keeps compliance risk contained

## Scope
- Ingest agreements (PDF/HTML) and build a retrieval index
- Answer questions with **exact clause citations**
- No automatic rule enforcement without human approval

## Guardrails
- Every answer must include citations (clause title + section + page)
- Show “not legal advice” disclaimer
- No auto‑execution; Q&A is advisory only
- Explicit confidence / “no result” fallback

## Data Flow
1) **Ingest** agreements → parse → normalize
2) **Chunk** by section/heading
3) **Embed** chunks; store in vector DB
4) **Retrieve** top‑k with filters (trade, version, date)
5) **Generate** response with citations

## Optional: Rule Drafting Mode
- User asks: “How does OT rotation work for Trade X?”
- System replies with citations + a proposed JSON rule draft
- Human approves before it’s added to ruleset

## UI
- Chat panel + citation drawer
- Quick filters: trade, agreement version, effective date

## Risks & Mitigations
- **Hallucination** → strict citation requirement
- **Outdated agreements** → versioned sources + warnings
- **Misinterpretation** → disclaimer + review workflow

## Implementation Notes
- Start with one agreement set (EPSCA)
- Use a lightweight vector store (e.g., sqlite + embeddings, or pgvector)
- Keep full PDF links for traceability

## Deliverables
- Agreement ingestion pipeline
- Search + chat UI with citations
- Rule‑drafting export (JSON) for manual review
