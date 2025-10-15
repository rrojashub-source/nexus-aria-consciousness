# ============================================
# NEXUS CEREBRO V2.0.0 - Dockerfile
# FASE 4 - DÍA 5: API + Workers
# ============================================
# Base: Python 3.11-slim
# Services: FastAPI API + Embeddings Worker
# ============================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="NEXUS VSCode"
LABEL version="2.0.0"
LABEL description="NEXUS Cerebro API + Workers"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${API_PORT:-8002}/health || exit 1

# Default command (override in docker-compose)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8002"]
