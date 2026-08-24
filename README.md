# BTG Robotics - Chapter Management Platform

Bridge the Gap Robotics Foundation website with a complete Chapter Management System. Built with Flask, SQLAlchemy, and Jinja2 templates.

## Tech Stack

- **Backend**: Python + Flask (Werkzeug, Jinja2) with Blueprint architecture
- **Database**: SQLite + SQLAlchemy ORM + Alembic migrations
- **Auth**: Session-based with password hashing, CSRF protection, rate limiting
- **Frontend**: HTML/CSS with responsive grid layouts, Google Fonts (Google Sans)
- **File Storage**: Local `static/uploads/` directory with magic-byte validation and EXIF stripping

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your own SECRET_KEY and passwords

# Run the application
python app.py
```

Opens at `http://localhost:2266`. The database and upload directories are auto-created on first run.

## Project Structure

```
.
├── app.py                    # Application entry point
├── btg/                      # Application package
│   ├── __init__.py           # create_app factory
│   ├── config.py             # Configuration (env vars, secrets)
│   ├── extensions.py         # db, csrf, migrate init
│   ├── models.py             # SQLAlchemy models (7 tables)
│   ├── auth.py               # Auth decorators, rate limiting
│   ├── blueprints/
│   │   ├── public.py         # Public routes (home, chapters, blog)
│   │   ├── auth_bp.py        # Auth routes (login, logout, change-password)
│   │   ├── admin.py          # Super admin routes
│   │   ├── dashboard.py      # Chapter president routes
│   │   └── secret.py         # Gated gokul007 panel
│   └── services/
│       └── upload.py         # File upload validation (magic bytes, EXIF strip)
├── templates/                # Jinja2 templates
│   ├── base.html
│   ├── home.html, login.html, change_password.html
│   ├── chapters/
│   ├── admin/
│   ├── dashboard/
│   └── errors/               # 404, 403, 500 error pages
├── static/
│   ├── css/style.css
│   ├── uploads/              # User-uploaded images
│   └── images/
├── data/                     # SQLite database + legacy JSON files
├── tests/                    # pytest integration tests
├── .env.example              # Environment variable template
├── .env                      # Local environment variables (git-ignored)
└── requirements.txt
```

## Database Models

Seven models with cascade deletes and foreign key constraints. See `btg/models.py` for full schema.

### Key Changes from v1
- `must_change_password` flag on User model forces password change on first login
- All child records cascade delete when a chapter is removed
- `delete_files()` method on models with uploaded files cleans up `static/uploads/`

## Security

- **CSRF Protection**: Flask-WTF protects every POST form. All templates include `{{ csrf_token() }}`.
- **Rate Limiting**: `/login` is rate-limited to 5 attempts per 60 seconds per IP.
- **Password Change**: New users have `must_change_password=True` and are redirected on first login.
- **Secret Panel**: `/gokul007` no longer auto-logins. Requires normal authentication. Direct URL visit redirects to `/login`.
- **Upload Validation**: Files validated by magic bytes (not just extension), capped at 4 MB, EXIF data stripped via Pillow.
- **Credentials**: Not hardcoded -- read from `.env` file via `python-dotenv`.
- **Error Pages**: Custom 404, 403, 500 templates with no debug tracebacks.

## Routes

All routes defined across 5 blueprints. Run `python run.py` and visit `/health` for a status check.

### Public
`/`, `/chapters`, `/chapters/<slug>`, `/kits`, `/partners`, `/events`, `/blog`, `/blog/<slug>`, `/contact`

### Auth
`/login`, `/logout`, `/change-password`

### Super Admin (`/admin/*`)
Dashboard, chapter CRUD, user management, legacy blog/events admin

### Chapter President (`/dashboard/*`)
Overview, about editor, team, events, gallery, announcements, applications, settings

### Secret Panel (`/gokul007/*`)
Requires super_admin login. Full system control: users, chapters, analytics, password resets.

## Testing

```bash
python -m pytest tests/ -v
```

Integration tests cover:
- Public page access
- Login success/failure
- Logout
- Route protection (redirects for unauthenticated users)
- No auto-login on `/gokul007`
- Role boundary enforcement (president cannot edit another chapter)

## Deployment

See [`deploy/README.md`](deploy/README.md) for a full walkthrough of running
this behind systemd + waitress on a Raspberry Pi, exposed via a Cloudflare
Tunnel.

Quick reference:

```bash
# Install production server (already in requirements.txt)
pip install waitress

# Run with waitress
FLASK_ENV=production waitress-serve --port=8000 --call btg:create_app
```

For production:
- Set `FLASK_ENV=production` — the app refuses to start in this mode with
  the default `SECRET_KEY` or without `BTG_ADMIN_PASSWORD` set
- Use a strong, unique `SECRET_KEY` via environment variable
- Set `BTG_ADMIN_PASSWORD` and `BTG_PRESIDENT_PASSWORD` via environment
- On a fresh database, the app creates all tables and seeds the admin user
  automatically on first run; run `flask db stamp head` once afterwards so
  later `flask db upgrade` calls apply cleanly (see `deploy/README.md`)
