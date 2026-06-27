import json
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from btg.extensions import db
from btg.models import User, Chapter, TeamMember, Event, GalleryImage, Announcement, Application

public = Blueprint('public', __name__)


# -- Homepage --


@public.route('/')
def home():
    highlights = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    chapters = Chapter.query.filter_by(published=True).order_by(Chapter.name).all()
    return render_template('home.html', highlights=highlights, chapters=chapters)


# -- Static informational pages --


@public.route('/kits')
def kits():
    return render_template('kits.html')


@public.route('/partners')
def partners():
    return render_template('partners.html')


@public.route('/contact')
def contact():
    return render_template('contact.html')


# -- Blog-style events (replaces legacy events and blog) --


@public.route('/events')
def events():
    all_events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('events.html', events=all_events)


@public.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('public.events'))
    chapter = db.session.get(Chapter, event.chapter_id) if event.chapter_id else None
    return render_template('events/detail.html', event=event, chapter=chapter)


@public.route('/blog')
def blog():
    return redirect(url_for('public.events'), 301)


@public.route('/blog/<path:post_id>')
def blog_post(post_id):
    return redirect(url_for('public.events'), 301)


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
