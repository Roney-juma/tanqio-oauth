#!/bin/sh
set -e

if [ -z "$SECRET_KEY" ]; then
	echo "ERROR: SECRET_KEY not set" >&2
	exit 1
fi

if [ "$SKIP_MIGRATIONS" != "1" ]; then
	echo "Applying database migrations..."
	python manage.py migrate --noinput
else
	echo "Skipping migrations (SKIP_MIGRATIONS=1)"
fi

if [ "$SKIP_COLLECTSTATIC" != "1" ]; then
	echo "Collecting static files..."
	python manage.py collectstatic --noinput || echo "Collectstatic skipped"
else
	echo "Skipping collectstatic (SKIP_COLLECTSTATIC=1)"
fi

echo "Starting application..."
exec "$@"