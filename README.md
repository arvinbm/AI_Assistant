# AI Assistant — Industrial Belt Assembly

An AI-powered document assistant built for an industrial belt assembly company. Allows technicians and staff to query internal product documentation, assembly manuals, and specifications using natural language.

Built with **Python**, **FastAPI**, **AWS Bedrock (Claude Haiku + Titan Embeddings)**, **FAISS**, and **Amazon S3**.

---

## Architecture

Documents (PDFs, manuals, spec sheets) are uploaded to **Amazon S3**, embedded using **Amazon Titan Embeddings** via AWS Bedrock, and indexed in a local **FAISS** vector store. At query time, the user's question is embedded with Titan, the top-k most relevant document chunks are retrieved from FAISS, and **Claude Haiku** (via AWS Bedrock) generates a grounded answer from those chunks.

```
User Query
    │
    ▼
Titan Embeddings (query vector)
    │
    ▼
FAISS Index (similarity search → top-k chunks)
    │
    ▼
Claude Haiku (RAG prompt → answer)
```

---

## Build Phases

### Phase 1 — Foundation *(Currently in progress)*
- Set up project structure and virtual environment
- Initialize FastAPI backend with health check endpoint
- Configure environment variables (`.env`) for AWS credentials, region, S3 bucket name
- Write `requirements.txt` and `Dockerfile`
- Set up `docker-compose.yml` with app and PostgreSQL services
- Initialize GitHub Actions CI workflow (lint + tests on push)

### Phase 2 — Document Ingestion Pipeline
- Build `/upload` endpoint that accepts PDF/DOCX files (assembly manuals, spec sheets)
- Store raw documents in Amazon S3 with metadata (filename, upload date, document type)
- Extract and chunk text from documents using `PyPDF2` / `pdfplumber`
- Generate chunk embeddings using Amazon Titan Embeddings via AWS Bedrock (`boto3`)
- Build and persist a FAISS index from the embedded chunks

### Phase 3 — RAG Query Pipeline
- Build `/chat` endpoint that accepts a natural language question
- Embed the query with Titan Embeddings and run similarity search against FAISS
- Retrieve top-k relevant chunks and construct a grounded RAG prompt
- Send prompt to Claude Haiku via AWS Bedrock and return the generated answer
- Add source attribution (which document + page each chunk came from)

### Phase 4 — Frontend
- Build a React/TypeScript chat interface with a message thread and input box
- Add a document upload panel tied to the `/upload` endpoint
- Display source citations alongside answers
- Style with Tailwind CSS; mobile-responsive layout

### Phase 5 — Production Deployment
- Deploy to Microsoft Azure using Docker Compose
- Configure environment-based settings for dev/staging/prod
- Add automated CD to Azure via GitHub Actions on merge to `main`
- Set up PostgreSQL on Azure for conversation and upload history

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI |
| Embeddings | Amazon Titan Embeddings (AWS Bedrock) |
| Generation | Claude Haiku (AWS Bedrock) |
| Vector Search | FAISS |
| Document Storage | Amazon S3 |
| Frontend | React, TypeScript, Tailwind CSS |
| Database | PostgreSQL |
| Infra | Docker, Docker Compose, Azure App Services |
| CI/CD | GitHub Actions |

---

## Getting Started (Phase 1)

```bash
git clone https://github.com/arvinbm/AI_Assistant.git
cd AI_Assistant
cp .env.example .env   # fill in AWS credentials, region, S3 bucket
docker compose up --build
```

The API will be available at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.
