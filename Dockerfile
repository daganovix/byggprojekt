# ── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python backend + built frontend ──────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy the built React app into /app/static
COPY --from=frontend-build /frontend/dist ./static

# Expose port (Railway injects $PORT at runtime)
EXPOSE 8000

# Seed DB then start server
CMD python seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
