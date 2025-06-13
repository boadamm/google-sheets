# Multi-stage Alpine-based Dockerfile for sheets-bot
# Following .cursorrules: Alpine-based, multi-stage, no secrets

# Build stage
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    build-base

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Install only production dependencies (exclude dev/test packages)
RUN pip install --no-cache-dir --user \
    watchdog==4.0.1 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    click==8.1.7 \
    gspread==6.1.2 \
    gspread-dataframe==3.3.1 \
    pyyaml==6.0.1 \
    tomli==2.0.1 \
    openpyxl==3.1.5

# Production stage
FROM python:3.11-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -s /sbin/nologin -G appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/ ./app/
COPY config/ ./config/
COPY cli.py ./cli.py

# Set ownership and permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER appuser

# Set PATH to include user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import app; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "app"] 