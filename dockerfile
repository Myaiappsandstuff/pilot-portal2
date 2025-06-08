# Use Python 3.11 slim image as base
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and use a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create final image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Create app directory and set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/uploads /app/monthly_reports \
    && chmod -R 755 /app/data /app/uploads /app/monthly_reports

# Create non-root user and set permissions
RUN groupadd -r flaskuser && useradd -r -g flaskuser -d /app -s /sbin/nologin flaskuser \
    && chown -R flaskuser:flaskuser /app \
    && chmod -R 755 /app

# Switch to non-root user
USER flaskuser

# Expose the port the app runs on
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--worker-class", "gevent", "--worker-connections", "1000", "--timeout", "120", "--keep-alive", "5", "app:app"]