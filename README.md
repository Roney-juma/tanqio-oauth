## Tanqio OAuth Service (Buildpack Deployment)

This project is a Django OAuth-enabled service (Django OAuth Toolkit + Social Auth) prepared for deployment on DigitalOcean App Platform **without Docker** using buildpacks.

### Key Files

- `manage.py` – Django runner.
- `oauth/` – Project settings & wsgi.
- `tanqio/` – Application code (views, OAuth validator, templates, static images).
- `requirements.txt` – Pinned dependencies (buildpack installs these).
- `.python-version` – Python version pin (preferred; replaces deprecated runtime.txt).
- `Procfile` – Run command (`gunicorn oauth.wsgi:application`).
- `.env.example` – Reference for environment variables to set in the platform.

Removed Docker artifacts (`Dockerfile`, `docker-compose.yml`, `entrypoint.sh`) to ensure the platform selects buildpacks automatically.

### Required Environment Variables

Set these in DigitalOcean (App > Settings > Environment Variables):

| Name                           | Required | Example / Notes                                |
| ------------------------------ | -------- | ---------------------------------------------- |
| SECRET_KEY                     | Yes      | Strong random string (don’t rotate casually)   |
| DEBUG                          | Yes      | `False` in production                          |
| ALLOWED_HOSTS                  | Yes      | `yourdomain.com` (comma separated if multiple) |
| CSRF_TRUSTED_ORIGINS           | Yes      | `https://yourdomain.com`                       |
| DATABASE*URL or POSTGRES*\*    | Yes      | Provided by managed Postgres or manual URL     |
| CORS_ALLOWED_ORIGINS           | Optional | e.g. `https://frontend.example`                |
| GOOGLE_OAUTH2_KEY / SECRET     | Optional | Social auth keys                               |
| GITHUB_KEY / GITHUB_SECRET     | Optional | Social auth keys                               |
| FACEBOOK_KEY / FACEBOOK_SECRET | Optional | Social auth keys                               |

Ephemeral SECRET_KEY generation only occurs during build or DEBUG=True; ensure a real one for runtime.

### First Deployment Steps

1. Push code to repository connected to DigitalOcean App Platform.
2. Create App (if not already) selecting the repo & branch.
3. Confirm detected build environment: Python buildpack (NOT Docker). If Docker is chosen, verify `Dockerfile` is absent (already removed).
4. Add environment variables above; attach Managed Postgres or set `DATABASE_URL`.
5. Deploy – buildpack installs dependencies and runs `collectstatic`.
6. Run migrations via App Platform Console (one-off command):
   ```
   python manage.py migrate --noinput
   ```
7. (Optional) Create superuser:
   ```
   python manage.py createsuperuser
   ```

### Local Development

Install dependencies and run dev server:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY=dev-secret DEBUG=True
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Health Check

Endpoint: `/api/health/` returns simple status for platform health probes.

### Static Files

Handled by WhiteNoise. `collectstatic` runs during build; ensure `STATIC_ROOT` is writable (default is fine).

### Security Notes

- Keep `DEBUG=False` in production.
- Always set explicit `ALLOWED_HOSTS` (avoid `*` long-term).
- Configure HTTPS (App Platform terminates TLS automatically).

### Future Enhancements

- Add CI workflow (lint/tests) before deploy.
- Separate release phase for migrations (App Platform can run a pre-deploy command once supported).
- Add monitoring/log aggregation.

---

For reinstating Docker support later, reintroduce a `Dockerfile` and (optionally) `entrypoint.sh` in a separate branch.
