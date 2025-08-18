web: gunicorn ${WSGI_MODULE:-oauth.wsgi}:application --bind 0.0.0.0:${PORT:-8080} --workers ${GUNICORN_WORKERS:-3} --timeout 120
# Optional release phase (uncomment if your platform supports it and you remove migrations from entrypoint):
# release: python manage.py migrate --noinput
