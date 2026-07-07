# --- Stage 1: build the React frontend ---
FROM node:22-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build          # outputs /frontend/dist

# --- Stage 2: the Python app (serves the API + the built frontend) ---
FROM python:3.12-slim
WORKDIR /app

# Python dependencies: base API + ML (embeddings, reranker, einops).
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

# App code and the built frontend (served by FastAPI at /).
COPY app/ ./app/
COPY --from=frontend /frontend/dist ./frontend/dist

# The knowledge base (uploads/, incl. the FAISS index) is provided at runtime
# via a mounted Azure Files volume; UPLOAD_DIR points at that mount path.
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
