# Operations & Service Desk — Streamlit demo image (non-root, slim).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EXTRACT_MODE=demo \
    CONNECTOR_MODE=fixture

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Shared platform (copied in at build time by docker-compose / CI; optional in demo)
# RUN pip install --no-cache-dir -e ../platform_core

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
