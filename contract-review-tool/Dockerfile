FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by pypdf and python-docx
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY migrations/ migrations/

# Create uploads directory
RUN mkdir -p uploads instance

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# ANTHROPIC_API_KEY and SECRET_KEY must be passed at runtime via --env or --env-file
ENV FLASK_ENV=production

CMD ["sh", "-c", "python -m gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 app:app"]
