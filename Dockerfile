# ─────────────────────────────────────────────────────────────
# AI-Coach – FastAPI + Supabase + HF, Python 3.11, slim image
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# 1. security: avoid running as root
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

# 2. install system libs (PDF parsing needs tesseract deps)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpoppler-cpp-dev \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 3. copy dependency list & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copy source code
COPY app/ app/
COPY app/main.py .

# 5. set env that tells uvicorn to use fewer workers (Cloud Run 1 CPU)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    UVICORN_CMD="uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1"

# 6. switch to non-root user
USER app

# 7. start
CMD ["/bin/sh", "-c", "$UVICORN_CMD"]
