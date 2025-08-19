web: bash -c 'mkdir -p staticfiles \
	&& if [ ! -f staticfiles/staticfiles.json ]; then echo "[startup] collecting static files"; python manage.py collectstatic --noinput || echo "collectstatic failed"; fi \
	&& exec gunicorn oauth.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120'
