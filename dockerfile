FROM python:3.11-slim

# Set environment variable for non-interactive tzdata install
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

# Set workdir
WORKDIR /app

# Install system deps (only what's necessary for builds)
RUN apt-get update && apt-get install -y \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static (just admin + DRF stuff)
RUN python manage.py collectstatic --noinput

# Run Gunicorn with Uvicorn worker
CMD ["gunicorn", "game.asgi:application", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2"]
