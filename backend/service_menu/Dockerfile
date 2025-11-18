# Multi-stage Dockerfile for Service Menu (Module 0)
# Optimized for production deployment with Google Cloud Storage and Vertex AI integration

# Stage 1: Base Python image with system dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for PostgreSQL and Google Cloud
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements file
COPY backend/service_menu/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy the entire backend directory (shared models/schemas)
COPY backend/ /app/backend/

# Create directory for Google Cloud credentials
RUN mkdir -p /app/credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port 8001 (Menu Service)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uvicorn", "backend.service_menu.main:app", "--host", "0.0.0.0", "--port", "8001"]
