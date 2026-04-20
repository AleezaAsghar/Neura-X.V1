# Neura-X

AI-powered healthcare platform built with Flask and configured for Vercel deployment.

## Project Structure

```
.
|-- app.py                 # Main Flask app (routes + business logic)
|-- api/index.py           # Vercel serverless entrypoint
|-- vercel.json            # Vercel build and route config
|-- requirements.txt
|-- .env.example
|-- scripts/               # Migration and utility scripts
|-- sql/                   # Database schema
|-- static/                # Frontend assets
`-- templates/             # Jinja templates
```

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill values.

Run locally:

```bash
python app.py
```

## Required Environment Variables

- `SECRET_KEY` (required in production)
- `SUPABASE_DB_URL` (recommended for production; SQLite fallback exists)
- `GROQ_API_KEY` (required for AI features)
- `HF_TOKEN` (optional)
- `SESSION_COOKIE_SECURE=true` (production)
- `TESSERACT_CMD` (optional custom binary path)

## Deploy to Vercel

1. Push this repository to GitHub.
2. Import the project into Vercel.
3. Set environment variables in Vercel Project Settings.
4. Deploy.

Vercel entrypoint is `api/index.py` and all routes are forwarded through `vercel.json`.

## Production Notes

- Vercel filesystem is ephemeral, so uploads are written to `/tmp` at runtime.
- For persistent files, use object storage (Supabase Storage, S3, etc.).
- Prefer Supabase Postgres in production. Do not rely on SQLite for scaled deployments.

## Security and Code Quality Updates

- Removed hardcoded/weak secret defaults from deployment docs and env template workflow.
- Replaced MD5 password generation with Werkzeug password hashing for new/updated passwords.
- Added backward-compatible login verification for legacy MD5 hashes.
- Removed duplicate environment loading flow.
- Removed non-Vercel deployment artifacts to keep repository clean.

## Supabase Migration

```bash
python scripts/migrate_sqlite_to_supabase.py --postgres-url "$SUPABASE_DB_URL"
```

Dry run:

```bash
python scripts/migrate_sqlite_to_supabase.py --postgres-url "$SUPABASE_DB_URL" --dry-run
```


