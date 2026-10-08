FROM python:3.12-slim

# Prevent Python from creating .pyc files
# and ensure logs are sent directly to stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install PostgreSQL client libraries and build dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code.
COPY . .

# Create directories required by Django.
RUN mkdir -p /app/staticfiles /app/media

# Create a non-root application user.
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Apply migrations, collect static files, then start Gunicorn.
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]