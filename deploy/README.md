# Deploying to a Raspberry Pi + Cloudflare

Runs as a long-lived process under systemd, served by waitress on
`127.0.0.1:8000`, exposed to your domain through a Cloudflare Tunnel (no
router port-forwarding needed).

## 1. Set up the app on the Pi

```bash
sudo useradd -m -s /bin/bash btg   # skip if you're running as your own user
sudo -u btg -i
git clone <your-repo-url> Bridge-The-Gap-Main-01
cd Bridge-The-Gap-Main-01

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   - SECRET_KEY: generate one, e.g. `python3 -c "import secrets; print(secrets.token_hex(32))"`
#   - FLASK_ENV=production
#   - BTG_ADMIN_EMAIL / BTG_ADMIN_PASSWORD: real admin login for this site
#   - BTG_PRESIDENT_PASSWORD: seed password for sample chapter presidents
nano .env

# First run creates the SQLite DB and all tables directly from the models,
# and seeds the admin user from BTG_ADMIN_EMAIL/BTG_ADMIN_PASSWORD. Ctrl+C
# once it's up and confirmed working.
.venv/bin/python app.py

# Mark the migration history as up to date against the schema you just
# created, so future `flask db upgrade` (after a `git pull`) applies only
# new migrations instead of re-running the whole history from scratch.
.venv/bin/flask db stamp head
```

The app config (`btg/config.py`) refuses to start with `FLASK_ENV=production`
unless `SECRET_KEY` and `BTG_ADMIN_PASSWORD` are actually set — if it exits
immediately on first run, check `.env`.

## 2. Install the systemd service

```bash
sudo cp deploy/btg.service /etc/systemd/system/btg.service
# Edit the User/WorkingDirectory/EnvironmentFile/ExecStart paths in the unit
# file if you didn't use /home/btg/Bridge-The-Gap-Main-01.
sudo systemctl daemon-reload
sudo systemctl enable --now btg
sudo systemctl status btg
```

Confirm it's up: `curl http://127.0.0.1:8000/health` should return `{"status": "ok"}`.

## 3. Expose it with a Cloudflare Tunnel

```bash
# Install cloudflared (see Cloudflare's docs for your Pi's architecture)
cloudflared tunnel login
cloudflared tunnel create btg-robotics
cloudflared tunnel route dns btg-robotics your-domain.com
```

Create `/etc/cloudflared/config.yml`:

```yaml
tunnel: btg-robotics
credentials-file: /home/btg/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: your-domain.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

Your domain now points at the Pi over Cloudflare's network — no inbound
ports need to be opened on your router, and TLS is handled by Cloudflare.

(If you'd rather run Cloudflare in DNS-only/proxy mode instead of a Tunnel,
you'd need to port-forward 443 on your router to a local reverse proxy
terminating TLS in front of `127.0.0.1:8000` — the Tunnel above avoids that
entirely, which is why it's the recommended path here.)

## 4. Updating the deployed site

```bash
sudo -u btg -i
cd Bridge-The-Gap-Main-01
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/flask db upgrade
exit
sudo systemctl restart btg
```

## Notes

- The SQLite database lives at `data/btg.db`. Back it up before upgrades:
  `cp data/btg.db data/btg.db.bak`.
- User-uploaded images live in `static/uploads/` — back that up too.
- Logs: `journalctl -u btg -f`.
