# BDG Chapters Map — Flask Integration

Drop-in files + snippets to add the interactive D3 chapters map to the
BTG Flask/SQLAlchemy/Jinja2 codebase. Data lives in your DB; editing is
gated behind your existing super-admin auth; CSRF is enforced.

## What goes where

| File in this folder | Copy to in your repo |
|---|---|
| `templates/chapters/map.html` | `templates/chapters/map.html` |
| `static/css/chapters-map.css` | `static/css/chapters-map.css` |
| `static/js/chapters-map.js`   | `static/js/chapters-map.js` |
| `static/vendor/*` (you download) | `static/vendor/` |

The `snippets/` folder is **not** copied wholesale — paste each piece
into the file named in its header.

## Install order

1. **Model** — paste the two columns from `snippets/1_models.py` into your
   `Chapter` model in `btg/models.py`.

2. **Migration** — run:
   ```
   flask db migrate -m "add chapter coordinates"
   flask db upgrade
   ```
   See `snippets/3_migration.py` if autogenerate misses the columns
   (SQLite needs `batch_alter_table`).

3. **Routes** — paste the three routes from `snippets/2_public_routes.py`
   into `btg/blueprints/public.py`. Wire `set_chapter_coordinates` to your
   real `super_admin_required` decorator. Confirm the endpoint names match
   what the template calls:
   - `public.chapters_map`
   - `public.chapters_geo`
   - `public.set_chapter_coordinates`
   - `public.chapter_detail`  (already exists — used to build chapter URLs)

4. **Templates/static** — copy `map.html`, `chapters-map.css`,
   `chapters-map.js` into place.

5. **Vendor the libs** — follow `snippets/6_vendoring_and_csp.md` to pull
   D3, topojson-client, and countries-110m.json into `static/vendor/`.

6. **Nav + base blocks** — add the nav link and confirm `{% block head %}`
   / `{% block scripts %}` exist in `base.html` (`snippets/4_base_html.html`).

7. **CSP** — if you serve a Content-Security-Policy, see the CSP + inline-
   script notes in `snippets/6_vendoring_and_csp.md`. Vendoring keeps
   everything on `'self'`; the one inline `window.BDG_MAP` script may need
   a nonce.

8. **Tests** — drop `snippets/7_tests.py` into `tests/`, adapt fixture
   names to your `conftest.py`, run `python -m pytest tests/ -v`.

## How it behaves

- **Visitors** see the map, hover pins for a tooltip, click for a popup
  with chapter name, president, and a link to the chapter page.
- **Super admins** additionally see a panel: pick a chapter, click
  "Place on map", click the globe to drop the pin (POSTs lat/lng).
  "Clear pin" removes a chapter's location without deleting the chapter.
- No `localStorage`, no `?admin=true`. Everything persists in the DB and
  is gated server-side.

## Assumptions to verify

- `Chapter` has `name`, `slug`, and a president value (`president` field
  or a relationship). If president is a relationship, edit `_president_name`
  in `snippets/2_public_routes.py`.
- You use a `current_user.is_super_admin` flag in templates. If your flag
  is named differently, update the two `{% if %}` checks in `map.html` and
  the `map-can-edit` meta tag.
- Flask-WTF CSRF accepts the `X-CSRFToken` header (default). If you set
  `WTF_CSRF_HEADERS`, make sure it still includes it.
