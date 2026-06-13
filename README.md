# AI Assistant

A production-ready AI assistant built with **Python**, **FastAPI**, and **AWS Bedrock**.

The assistant uses a retrieval-augmented generation (RAG) architecture to answer questions from uploaded documents, with a React/TypeScript frontend and full CI/CD deployment on Microsoft Azure.

---

## Build Phases

### Phase 1 — Foundation *(Currently in progress)*
- Set up project structure and virtual environment
- Initialize FastAPI backend with health check endpoint
- Configure environment variables (`.env`) for AWS credentials and region
- Write `requirements.txt` and `Dockerfile`
- Set up `docker-compose.yml` with app and PostgreSQL services
- Initialize GitHub Actions CI workflow (lint + tests on push)

### Phase 2 — LLM Integration
- Connect to AWS Bedrock using `boto3`
- Implement a `/chat` endpoint that sends prompts to a Bedrock foundation model
- Add structured error handling for all AWS `ClientError` responses
- Write unit tests for the chat endpoint with mocked Bedrock calls

### Phase 3 — RAG Pipeline
- Create a document ingestion endpoint (`/upload`) that accepts PDF/TXT files
- Store documents in Amazon S3 and index them in a Bedrock Knowledge Base
- Modify `/chat` to retrieve relevant document chunks before generating a response
- Add DEBUG-level logging to inspect the full prompt sent to the model

### Phase 4 — Frontend
- Build a React/TypeScript chat interface with a message thread and input box
- Connect to the FastAPI backend via REST API
- Add a document upload panel tied to the `/upload` endpoint
- Style with Tailwind CSS; mobile-responsive layout

### Phase 5 — Production Deployment
- Deploy to Microsoft Azure using Docker Compose
- Configure environment-based settings for dev/staging/prod
- Add automated CD to Azure via GitHub Actions on merge to `main`
- Set up PostgreSQL on Azure for conversation history persistence

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI |
| AI / LLM | AWS Bedrock, boto3 |
| RAG | Amazon S3, Bedrock Knowledge Bases |
| Frontend | React, TypeScript, Tailwind CSS |
| Database | PostgreSQL |
| Infra | Docker, Docker Compose, Azure App Services |
| CI/CD | GitHub Actions |

---

## Getting Started (Phase 1)

```bash
git clone https://github.com/arvinbm/AI_Assistant.git
cd AI_Assistant
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.
