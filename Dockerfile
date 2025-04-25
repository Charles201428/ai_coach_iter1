# ────────────────────────────────────────────────
# AI-Coach backend – FastAPI + Supabase + HF
# Python 3.11 slim, ready for Google Cloud Run
# ────────────────────────────────────────────────
FROM python:3.11-slim AS base

# 1. for reproducible builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 2. create non-root user & group  (security best-practice on Cloud Run)
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

# 3. copy dependency list & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copy source code  (everything inside app/)
COPY app/ app/

# 5. switch to non-root user
USER app

# 6. start FastAPI via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
