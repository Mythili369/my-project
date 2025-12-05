# -----------------------
# Stage 1: Builder
# -----------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies into /install
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# -----------------------
# Stage 2: Runtime
# -----------------------
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Install procps so ps and pgrep are available
RUN apt-get update && apt-get install -y procps && apt-get clean && rm -rf /var/lib/apt/lists/*


# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# -----------------------
# Copy scripts folder and make scripts executable
# -----------------------
COPY scripts /app/scripts
RUN chmod +x /app/scripts/*.py

# -----------------------
# Setup 2FA cron job
# -----------------------
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# -----------------------
# Create volume mount points
# -----------------------
RUN mkdir -p /data /cron && chmod 755 /data /cron

# -----------------------
# Copy seed.txt into /data so cron script can read it
# -----------------------
COPY seed.txt /data/seed.txt

# Ensure cron log file exists
RUN touch /cron/last_code.txt

# Expose API port
EXPOSE 8080

# Start cron service and API server
CMD cron && python -m uvicorn api_server:app --host 0.0.0.0 --port 8080
