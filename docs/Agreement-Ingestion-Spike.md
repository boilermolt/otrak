# Agreement Ingestion Spike (EPSCA)

## Goal
Identify and ingest the relevant collective bargaining agreements, then prepare them for RAG with stable citations.

## Findings (initial)
- EPSCA resources page appears to serve documents dynamically (trade selector). A browser session is likely required to list all trade agreements.
- We need the **specific trade agreements** you want indexed (trade list + effective dates/versions).

## Plan
1) **Collect source files**
   - Obtain PDFs (preferred) or HTML for each agreement.
   - Capture metadata: trade, version/effective date, source URL.

2) **Normalize**
   - Convert to text + preserve page numbers.
   - Store alongside original PDF for auditability.

3) **Chunking strategy**
   - Split by section headings.
   - Keep clause IDs + page numbers in chunk metadata.

4) **Index**
   - Build embeddings + vector index.
   - Store full citation fields: {trade, agreement_version, section, page, url}.

5) **QA + citation enforcement**
   - Retrieval must return only chunks with citations.
   - Q&A UI shows source links and page numbers.

## Inputs needed
- Which trades to include first
- Agreement PDFs or exact URLs
- Effective date/version requirements

## Deliverables
- `/data/agreements/` folder structure
- `agreements_index.json` metadata
- RAG-ready chunk files
