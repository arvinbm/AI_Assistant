# AI Assistant — Industrial Belt Assembly

An AI-powered document assistant built for an industrial belt assembly company. It lets technicians and staff query internal product documentation, assembly manuals, customer records, and specifications in natural language — in **Persian (Farsi), English, or a mix of both**.

Built with **Python**, **FastAPI**, a local **multilingual embedding model (BGE-m3)**, **FAISS**, **Amazon S3**, and **Claude Haiku (AWS Bedrock)** for answer generation.

---

## Architecture

Documents are extracted to text, **normalized**, split into chunks, embedded with a **multilingual model (BGE-m3)**, and indexed in a **FAISS** vector store (persisted to S3 or locally). At query time the question is normalized and embedded the same way, the closest chunks are retrieved from FAISS, **reranked** with a cross-encoder, and the best are passed to **Claude Haiku**, which generates a grounded, cited answer.

```
Ingestion:   document → extract (PyMuPDF) → normalize (Farsi) → chunk
                      → embed (BGE-m3) → FAISS index (+ chunk text/source/lang)

Query:       question → normalize → embed (BGE-m3)
                      → FAISS top-30 → rerank (cross-encoder) → top-8
                      → Claude Haiku → grounded answer + citations
```

Raw files live in **Amazon S3**; the FAISS index + metadata are persisted there too, so the deployed app loads a pre-built index on startup and never needs the original corpus.

---

## Multilingual (Farsi / English) handling

The corpus is **mixed-language**: some documents are English (product data sheets), some are Persian (customer records, the product catalog), and **many individual documents contain both** (Persian prose with English part numbers, model codes, and terms). This is the central challenge of the project, addressed by:

- **Persian text normalization** — Persian text appears in inconsistent forms (Arabic vs Persian yeh/kaf, Arabic-Indic vs Persian digits, ZWNJ, diacritics, tatweel). The same word written two ways silently fails to match. All text is normalized to one canonical form, applied to **both documents and queries**. ASCII (English words, part numbers) is left untouched.
- **Unified cross-lingual embeddings** — instead of partitioning by language (which breaks on mixed chunks), everything is embedded into **one shared semantic space** with **BGE-m3**, a multilingual model. This was validated on the real corpus: Farsi→Farsi, English→English, **English↔Farsi cross-lingual**, and mixed-chunk retrieval all work. A Persian question can surface the relevant English data sheet and vice-versa.
- **Language tagging** — each chunk is tagged `fa` / `en` / `mixed` / `unknown` in its metadata for debugging and optional weighting (not a hard filter).
- **Reranking** — a multilingual cross-encoder reranker (BGE-reranker-v2-m3) re-scores the top candidates for sharper relevance across languages.

Scanned / image-only PDFs (no extractable text) are skipped by design (no OCR), except the product catalog, which was OCR'd once into a searchable text sidecar.

---

## Embedding backend (pluggable)

The embedding layer is selected via `EMBEDDING_BACKEND`:

| Value | Backend | Cost |
|-------|---------|------|
| `multilingual` *(default for real use)* | local **BGE-m3** (1024-dim) | Free, runs locally, no AWS |
| `bedrock` | Amazon Titan Embeddings | Paid (AWS) |
| `local` *(default in code, for tests/CI)* | deterministic pseudo-embedding | Free, not semantic |

Embeddings run **locally for free**; AWS is only used for **Claude Haiku generation**.

---

## Build Phases

### Phase 1 — Foundation ✅
- FastAPI backend with health check, env-based config, `Dockerfile`, `docker-compose.yml`, GitHub Actions CI (lint + tests).

### Phase 2 — Document Ingestion Pipeline *(in progress)*
- Extract text from PDFs with **PyMuPDF**; skip scanned/empty docs (no OCR).
- **Normalize** Persian/mixed text; split into overlapping chunks.
- Embed chunks with **BGE-m3**; store raw files in S3/local; tag each chunk with its language.
- Build and persist a **FAISS** index (+ chunk text/source/lang) to S3/local.
- Bulk-ingest the base corpus (one-time) and accept ongoing **`/upload`s**.

### Phase 3 — RAG Query Pipeline
- `/chat` endpoint: normalize + embed the question, retrieve **top-30** from FAISS, **rerank** to **top-8**, build a grounded prompt, and answer with **Claude Haiku**.
- Source attribution (which document each chunk came from); relevance threshold to avoid answering off-topic questions.

### Phase 4 — Frontend
- React/TypeScript chat interface + document upload panel, source citations, Tailwind CSS, mobile-responsive.

### Phase 5 — Production Deployment
- Deploy to Microsoft Azure via Docker Compose; env-based settings; automated CD via GitHub Actions on merge to `main`.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI |
| Text extraction | PyMuPDF |
| Embeddings | BGE-m3 (local, multilingual) — Titan optional |
| Vector search | FAISS |
| Reranking | BGE-reranker-v2-m3 (multilingual cross-encoder) |
| Generation | Claude Haiku (AWS Bedrock) |
| Document storage | Amazon S3 (local-folder fallback) |
| Frontend | React, TypeScript, Tailwind CSS |
| Infra | Docker, Docker Compose, Azure App Services |
| CI/CD | GitHub Actions |

---

## Getting Started

```bash
git clone https://github.com/arvinbm/AI_Assistant.git
cd AI_Assistant
cp .env.example .env            # configure backend, AWS (for generation), etc.
pip install -r requirements.txt
pip install -r requirements-ml.txt   # for the local multilingual embedding backend
docker compose up --build
```

The API will be available at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.
