# Site24x7 CLI AI Agent - Docker Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies with retries and fallbacks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    pydantic-settings \
    python-multipart \
    jinja2 \
    openai \
    requests \
    beautifulsoup4 \
    trafilatura \
    pygithub \
    apscheduler \
    gitpython

# Copy application files
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/data && \
    chmod +x /app/main.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/status || exit 1

# Run the application
CMD ["python", "main.py"]