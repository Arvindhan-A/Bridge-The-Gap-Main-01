import json
import math
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from btg.extensions import db
from btg.models import (User, Chapter, TeamMember, Event, EventImage, GalleryImage,
                        Announcement, Application, Sponsor, SiteStat,
                        Curriculum, Advisor, AdvisorInitiative, Subscriber)

public = Blueprint('public', __name__)

# Cached world atlas data for homepage map
_world_atlas_cache = None


def _get_world_atlas():
    global _world_atlas_cache
    if _world_atlas_cache is None:
        try:
            import urllib.request
            url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
            with urllib.request.urlopen(url, timeout=10) as r:
                _world_atlas_cache = json.loads(r.read())
        except Exception:
            _world_atlas_cache = {}
    return _world_atlas_cache


def _decode_arcs(topology):
    """Decode TopoJSON arcs to lists of [lng, lat] coordinates."""
    if not topology or 'arcs' not in topology:
        return []
    transform = topology.get('transform', {})
    scale_x, scale_y = transform.get('scale', [1, 1])
    trans_x, trans_y = transform.get('translate', [0, 0])
    decoded = []
    for arc in topology['arcs']:
        points = []
        x, y = 0, 0
        for dx, dy in arc:
            x += dx
            y += dy
            lng = x * scale_x + trans_x
            lat = y * scale_y + trans_y
            points.append([lng, lat])
        decoded.append(points)
    return decoded


def _flatten_arcs(arc_indices):
    """Recursively flatten TopoJSON arc indices to a list of integers."""
    result = []
    for item in arc_indices:
        if isinstance(item, list):
            result.extend(_flatten_arcs(item))
        else:
            result.append(item)
    return result


def _collect_rings(node):
    """Return the polygon rings in a TopoJSON geometry's `arcs`.

    A ring is a flat list of arc indices; Polygon nests them one level and
    MultiPolygon two, so recurse until we hit a list of plain ints.
    """
    if not isinstance(node, list) or not node:
        return []
    if all(isinstance(i, int) for i in node):
        return [node]
    rings = []
    for item in node:
        rings.extend(_collect_rings(item))
    return rings


def _arc_to_svg_path(arc_indices, decoded_arcs):
    """Convert TopoJSON arc references to an SVG path d string (equirectangular).

    Each ring is emitted as ONE closed subpath: the arcs that make it up are
    stitched together first, then closed. Closing per-arc instead would fill
    spurious wedges between the ends of consecutive arcs.
    """
    W, H = 960, 480
    parts = []
    for ring in _collect_rings(arc_indices):
        points = []
        for idx in ring:
            if idx < 0:
                arc = list(reversed(decoded_arcs[~idx]))
            else:
                arc = decoded_arcs[idx]
            # consecutive arcs share an endpoint - drop the duplicate
            if points and arc and points[-1] == arc[0]:
                points.extend(arc[1:])
            else:
                points.extend(arc)
        if len(points) < 3:
            continue
        # skip rings that wrap the antimeridian; they smear across the map
        if any(abs(points[i][0] - points[i - 1][0]) > 180 for i in range(1, len(points))):
            continue
        for i, (lng, lat) in enumerate(points):
            x = (lng + 180) / 360 * W
            y = (90 - lat) / 180 * H
            parts.append(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}")
        parts.append("Z")
    return " ".join(parts)


def _point_in_polygon(lng, lat, polygon):
    """Ray-casting point-in-polygon test."""
    x, y = lng, lat
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside


def _get_arc_points(arc_idx, decoded_arcs):
    """Get decoded coordinate list for an arc (handles negative indices for reverse)."""
    if arc_idx < 0:
        idx = ~arc_idx
        return list(reversed(decoded_arcs[idx]))
    return decoded_arcs[arc_idx]


def _ring_points(ring, decoded_arcs):
    """Stitch a ring's arcs into one closed coordinate list."""
    points = []
    for idx in ring:
        arc = _get_arc_points(idx, decoded_arcs)
        if points and arc and points[-1] == arc[0]:
            points.extend(arc[1:])
        else:
            points.extend(arc)
    return points


def _country_contains_point(geom, decoded_arcs, pt_lng, pt_lat):
    """Check if a TopoJSON geometry contains a point.

    Tests against each fully stitched ring - a single arc is only a fragment
    of a border, so testing one arc alone gives meaningless results.
    """
    for ring in _collect_rings(geom.get('arcs', [])):
        points = _ring_points(ring, decoded_arcs)
        if len(points) >= 3 and _point_in_polygon(pt_lng, pt_lat, points):
            return True
    return False


_map_svg_cache = {}


def _render_world_map_svg(topology, chapter_points, hue=262, W=960, H=480):
    """Return an SVG string of the world map with highlighted chapter countries.

    Decoding the whole topology is expensive, so the finished markup is cached
    against the chapter coordinates that produced it.
    """
    cache_key = tuple(sorted((round(x, 3), round(y, 3)) for x, y in chapter_points))
    if cache_key in _map_svg_cache:
        return _map_svg_cache[cache_key]

    decoded = _decode_arcs(topology)
    if not decoded:
        return ""

    objects = topology.get('objects', {})
    countries_data = None
    for key in objects:
        obj = objects[key]
        if obj.get('type') == 'GeometryCollection':
            countries_data = obj.get('geometries', [])
            break
    if not countries_data:
        return ""

    # Determine which country indices contain chapter points
    highlighted = set()
    for i, geom in enumerate(countries_data):
        for pt_lng, pt_lat in chapter_points:
            if _country_contains_point(geom, decoded, pt_lng, pt_lat):
                highlighted.add(i)
                break

    parts = []
    for i, geom in enumerate(countries_data):
        d = _arc_to_svg_path(geom.get('arcs', []), decoded)
        if not d:
            continue
        is_hl = i in highlighted
        cls = 'wm-country wm-on' if is_hl else 'wm-country'
        parts.append(f'<path d="{d}" class="{cls}"/>')
    svg = "".join(parts)
    _map_svg_cache[cache_key] = svg
    return svg


def _project_equirect(lng, lat, W=960, H=480):
    """Same projection used by _arc_to_svg_path, so pins line up with the paths."""
    return ((lng + 180) / 360 * W, (90 - lat) / 180 * H)


def _spread_pins(pins, min_gap=16, iterations=60):
    """Nudge overlapping pins apart, keeping the true anchor for a leader line."""
    for _ in range(iterations):
        moved = False
        for i in range(len(pins)):
            for j in range(i + 1, len(pins)):
                a, b = pins[i], pins[j]
                dx, dy = b['x'] - a['x'], b['y'] - a['y']
                dist = math.hypot(dx, dy)
                if dist >= min_gap:
                    continue
                if dist == 0:
                    dx, dy = (0.6 if i % 2 else -0.6), 0.6
                    dist = math.hypot(dx, dy)
                push = (min_gap - dist) / 2
                ux, uy = dx / dist, dy / dist
                a['x'] -= ux * push; a['y'] -= uy * push
                b['x'] += ux * push; b['y'] += uy * push
                moved = True
        if not moved:
            break
    return pins


# -- Homepage --


@public.route('/')
def home():
    chapters = Chapter.query.filter_by(published=True).order_by(Chapter.name).all()
    chapter_points = [(ch.longitude or 0, ch.latitude or 0) for ch in chapters]
    world_atlas = _get_world_atlas()
    map_svg = _render_world_map_svg(world_atlas, chapter_points)
    highlights = Event.query.order_by(Event.created_at.desc()).limit(3).all()
    stat = SiteStat.get()
    gallery = (EventImage.query.join(Event)
               .order_by(Event.created_at.desc(), EventImage.display_order)
               .limit(8).all())
    sponsors = (Sponsor.query.filter_by(published=True)
                .order_by(Sponsor.display_order, Sponsor.name).all())

    # Pins for the homepage map, projected into the same 960x480 space as map_svg
    map_pins = []
    for ch in chapters:
        if ch.latitude is None or ch.longitude is None:
            continue
        x, y = _project_equirect(ch.longitude, ch.latitude)
        map_pins.append({
            'x': x, 'y': y, 'ax': x, 'ay': y,
            'name': ch.name, 'city': ch.city or '',
            'status': ch.status or 'active',
            'url': url_for('public.chapter_detail', slug=ch.slug),
        })
    _spread_pins(map_pins)

    return render_template('home.html', chapters=chapters,
                           world_map_svg=map_svg, highlights=highlights, stat=stat,
                           gallery=gallery, sponsors=sponsors, map_pins=map_pins)


# -- Static informational pages --


@public.route('/kits')
def kits():
    return render_template('kits.html')


@public.route('/partners')
def partners():
    sponsors = Sponsor.query.filter_by(published=True).order_by(Sponsor.display_order, Sponsor.name).all()
    return render_template('partners.html', sponsors=sponsors)


@public.route('/contact')
def contact():
    return render_template('contact.html')


@public.route('/programs')
def programs():
    today = date.today()
    upcoming = (Event.query.filter(Event.date >= today)
                .order_by(Event.date).limit(6).all())
    return render_template('programs.html', upcoming_events=upcoming)


@public.route('/curriculum')
def curriculum():
    items = (Curriculum.query.filter_by(published=True)
             .order_by(Curriculum.display_order, Curriculum.title).all())
    return render_template('curriculum.html', items=items)


@public.route('/gallery')
def gallery():
    images = (EventImage.query.join(Event)
              .order_by(Event.date.desc(), EventImage.display_order).all())
    # one filter tab per event that actually has photos
    events = []
    seen = set()
    for img in images:
        if img.event and img.event.id not in seen:
            seen.add(img.event.id)
            events.append(img.event)
    return render_template('gallery.html', images=images, events=events)


@public.route('/board')
def board():
    advisors = (Advisor.query.filter_by(published=True)
                .order_by(Advisor.display_order, Advisor.name).all())
    return render_template('board.html', advisors=advisors)


@public.route('/board/<slug>')
def advisor_detail(slug):
    advisor = Advisor.query.filter_by(slug=slug, published=True).first_or_404()
    initiatives = advisor.initiatives.order_by(AdvisorInitiative.display_order).all()
    return render_template('advisor_detail.html', advisor=advisor, initiatives=initiatives)


@public.route('/subscribe', methods=['POST'])
def subscribe():
    email = (request.form.get('email') or '').strip().lower()
    source = (request.form.get('source') or '').strip()
    if not email or '@' not in email:
        flash('Please enter a valid email address.', 'error')
    elif Subscriber.query.filter_by(email=email).first():
        flash("You're already subscribed — thanks!", 'success')
    else:
        db.session.add(Subscriber(email=email, source=source))
        db.session.commit()
        flash("Thanks! You're on the list.", 'success')
    return redirect(request.referrer or url_for('public.home'))



# -- Public events (all chapters) --


@public.route('/events')
def events():
    all_events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('events.html', events=all_events)


# -- Blog (posts = events not tied to a chapter) --


@public.route('/blog')
def blog():
    posts = Event.query.filter(Event.chapter_id.is_(None)).order_by(Event.created_at.desc()).all()
    return render_template('blog.html', posts=posts)


@public.route('/blog/<int:event_id>')
def blog_post(event_id):
    post = Event.query.filter_by(id=event_id, chapter_id=None).first_or_404()
    images = post.images.order_by(EventImage.display_order).all()
    return render_template('blog_post.html', post=post, images=images)


@public.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    images = event.images.order_by(EventImage.display_order).all()
    return render_template('event_detail.html', event=event, images=images)


# -- Public chapters --


@public.route('/chapters')
def chapters_list():
    all_chapters = Chapter.query.filter_by(published=True).order_by(Chapter.name).all()
    chapters_data = []
    for ch in all_chapters:
        pres = User.query.filter_by(chapter_id=ch.id, role='chapter_president').first()
        chapters_data.append({
            'id': ch.slug,
            'name': ch.name,
            'president': pres.name if pres else 'TBD',
            'url': url_for('public.chapter_detail', slug=ch.slug),
            'lat': ch.latitude or 0,
            'lng': ch.longitude or 0,
            'status': ch.status or 'active',
            'city': ch.city or '',
            'timezone': ch.timezone or '',
        })
    president_map = {}
    for u in User.query.filter_by(role='chapter_president').all():
        president_map[u.chapter_id] = u.name
    return render_template('chapters/map.html', chapters=all_chapters, president_map=president_map, chapters_json=json.dumps(chapters_data))


@public.route('/chapters/<slug>')
def chapter_detail(slug):
    chapter = Chapter.query.filter_by(slug=slug, published=True).first_or_404()
    team = TeamMember.query.filter_by(chapter_id=chapter.id).order_by(TeamMember.display_order).all()
    now = date.today()
    upcoming = Event.query.filter(
        Event.chapter_id == chapter.id,
        Event.date >= now,
        Event.status != 'completed'
    ).order_by(Event.date).all()
    past = Event.query.filter(
        Event.chapter_id == chapter.id,
        Event.date < now
    ).order_by(Event.date.desc()).all()
    gallery = GalleryImage.query.filter_by(chapter_id=chapter.id).order_by(GalleryImage.display_order).all()
    announcements = Announcement.query.filter_by(chapter_id=chapter.id).order_by(
        Announcement.pinned.desc(), Announcement.created_at.desc()
    ).all()
    return render_template(
        'chapters/detail.html',
        chapter=chapter, team=team,
        upcoming_events=upcoming, past_events=past,
        gallery=gallery, announcements=announcements
    )


@public.route('/chapters/<slug>/apply')
def chapter_apply_page(slug):
    chapter = Chapter.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('chapters/apply.html', chapter=chapter)


@public.route('/chapters/<slug>/join', methods=['POST'])
def chapter_apply(slug):
    chapter = Chapter.query.filter_by(slug=slug).first_or_404()
    app_record = Application(
        chapter_id=chapter.id,
        applicant_name=request.form.get('name', ''),
        email=request.form.get('email', ''),
        school=request.form.get('school', ''),
        city=request.form.get('city', ''),
        interests=request.form.get('interests', ''),
        motivation=request.form.get('motivation', ''),
    )
    db.session.add(app_record)
    db.session.commit()
    flash('Application submitted! We will reach out soon.', 'success')
    return redirect(url_for('public.chapter_detail', slug=slug))
