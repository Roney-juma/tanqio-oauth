FROM python:3.13-slim-bookworm AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# System build deps (removed later for slimmer final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
		curl \
		libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=oauth.settings
RUN python manage.py collectstatic --noinput || echo "Collectstatic skipped"

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install minimal runtime dependencies for psycopg2 (libpq) and SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
		libpq5 \
		ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app

ENV DJANGO_SETTINGS_MODULE=oauth.settings \
	PORT=8000

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "oauth.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
