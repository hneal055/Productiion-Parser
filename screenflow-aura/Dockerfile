FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY app.py .
COPY templates/ templates/
COPY migrations/ migrations/

RUN mkdir -p instance

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8083

# ANTHROPIC_API_KEY, SECRET_KEY, AURA_API_KEY must be passed at runtime
ENV FLASK_ENV=production

CMD ["sh", "-c", "python -m gunicorn --bind 0.0.0.0:${PORT:-8083} --workers 1 --timeout 120 app:app"]
