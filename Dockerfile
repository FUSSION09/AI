# Multi-Stage Production Container for Apex Autonomous System (MSMG)
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/cache/huggingface \
    TORCH_HOME=/app/cache/torch

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and configurations
COPY src/ /app/src/
COPY configs/ /app/configs/
COPY data/ /app/data/
COPY ui/ /app/ui/

# Expose FastAPI MSMG port & Prometheus metrics port
EXPOSE 8000 9090

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/control/telemetry || exit 1

ENTRYPOINT ["python", "src/gateway_api.py"]

