# ================================================================
# 2) ROUTES  —  add to btg/blueprints/public.py
# ----------------------------------------------------------------
# Three routes:
#   GET  /chapters/map            -> renders the map page
#   GET  /api/chapters/geo        -> JSON feed of placed chapters
#   POST /chapters/<id>/coordinates -> super-admin writes lat/lng
#
# Adjust imports to match your project. The names assumed here:
#   from btg.extensions import db
#   from btg.models import Chapter
#   from btg.auth import super_admin_required   # your existing decorator
#   from flask_login import current_user        # or however you expose it
#
# If you DON'T use flask_login, replace `current_user` checks with
# whatever your session-auth helper is (the template uses the same
# `current_user.is_super_admin` flag — keep them consistent).
# ================================================================

from flask import render_template, jsonify, request, abort, url_for

# from . import public_bp   # however your blueprint object is named
# from btg.extensions import db
# from btg.models import Chapter
# from btg.auth import super_admin_required


def _president_name(chapter):
    """Resolve a president display name.
    If you store president directly on Chapter, just use chapter.president.
    If it's a relationship (e.g. chapter.president_user.name), adapt here.
    """
    name = getattr(chapter, "president", None)
    if name:
        return name
    user = getattr(chapter, "president_user", None)
    if user:
        return getattr(user, "name", None) or getattr(user, "username", None)
    return "TBD"


@public_bp.route("/chapters/map")
def chapters_map():
    chapters = Chapter.query.order_by(Chapter.name.asc()).all()
    chapters_have_pins = any(c.latitude is not None and c.longitude is not None
                             for c in chapters)
    return render_template(
        "chapters/map.html",
        chapters=chapters,
        chapters_have_pins=chapters_have_pins,
    )


@public_bp.route("/api/chapters/geo")
def chapters_geo():
    """Public JSON feed — only chapters that have coordinates."""
    placed = (Chapter.query
              .filter(Chapter.latitude.isnot(None))
              .filter(Chapter.longitude.isnot(None))
              .all())
    payload = [{
        "id":        c.id,
        "name":      c.name,
        "president": _president_name(c),
        "url":       url_for("public.chapter_detail", slug=c.slug),
        "lat":       c.latitude,
        "lng":       c.longitude,
    } for c in placed]
    return jsonify(chapters=payload)


@public_bp.route("/chapters/<int:chapter_id>/coordinates", methods=["POST"])
@super_admin_required          # <-- your existing decorator; enforces auth + role
def set_chapter_coordinates(chapter_id):
    """Set or clear a chapter's map coordinates.
    CSRF is enforced by Flask-WTF on this POST (the JS sends X-CSRFToken).
    Send {"latitude": <float|null>, "longitude": <float|null>} as JSON.
    """
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json(silent=True) or {}

    lat = data.get("latitude")
    lng = data.get("longitude")

    # Allow explicit clearing (both null).
    if lat is None and lng is None:
        chapter.latitude = None
        chapter.longitude = None
    else:
        try:
            lat = float(lat); lng = float(lng)
        except (TypeError, ValueError):
            abort(400, description="latitude and longitude must be numbers")
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            abort(400, description="coordinates out of range")
        chapter.latitude = lat
        chapter.longitude = lng

    db.session.commit()
    return jsonify(ok=True, id=chapter.id,
                   latitude=chapter.latitude, longitude=chapter.longitude)


# ----------------------------------------------------------------
# CSRF NOTE
# ----------------------------------------------------------------
# Flask-WTF's CSRFProtect validates the X-CSRFToken header automatically
# for JSON POSTs as long as WTF_CSRF_HEADERS includes "X-CSRFToken"
# (it does by default). The template exposes the token via a <meta> tag,
# and chapters-map.js sends it. No per-route exemption needed — do NOT
# add @csrf.exempt here.
