import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from btg.extensions import db
from btg.models import (User, Chapter, TeamMember, Event, EventImage, GalleryImage,
                        Announcement, Application, Role, AuditLog, UserSession, Sponsor,
                        SiteStat, Curriculum, Advisor, AdvisorInitiative, Subscriber)
from btg.auth import super_admin_required
from btg.services.upload import save_upload, delete_upload
from btg.blueprints._shared import (
    log_audit, create_user_from_form, update_user_from_form, delete_user_by_id,
    delete_chapter_by_id, toggle_chapter_published,
    create_role_from_form, update_role_from_form, delete_role_by_id,
)

admin = Blueprint('admin', __name__)


def try_float(val):
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None


def try_int(val):
    try:
        return int(val) if val not in (None, '') else None
    except (ValueError, TypeError):
        return None


def strip_tags(html):
    return re.sub(r'<[^>]+>', ' ', html or '').strip()


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9-]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# -- Dashboard --


@admin.route('/admin')
@super_admin_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    if user.role == 'chapter_president':
        return redirect(url_for('dashboard.overview'))
    from btg.models import GalleryImage
    chapters = Chapter.query.order_by(Chapter.name).all()
    users = User.query.order_by(User.name).all()
    all_members = TeamMember.query.count()
    all_events = Event.query.count()
    all_gallery = GalleryImage.query.count()
    all_apps = Application.query.count()
    return render_template(
        'admin/dashboard.html',
        chapters=chapters, users=users,
        all_members=all_members, all_events=all_events,
        all_gallery=all_gallery, all_apps=all_apps
    )


# -- Chapter CRUD --


@admin.route('/admin/chapters')
@super_admin_required
def chapters():
    chapters = Chapter.query.order_by(Chapter.name).all()
    return render_template('admin/chapters.html', chapters=chapters)


@admin.route('/admin/chapters/create', methods=['GET', 'POST'])
@super_admin_required
def chapter_create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        if not name or not city:
            flash('Name and city are required.', 'error')
            return render_template('admin/chapter_form.html', chapter=None)

        slug_base = slugify(name)
        slug = slug_base
        counter = 1
        while Chapter.query.filter_by(slug=slug).first():
            slug = f'{slug_base}-{counter}'
            counter += 1

        chapter = Chapter(
            slug=slug, name=name, city=city,
            description=request.form.get('description', ''),
            about=request.form.get('about', ''),
            mission=request.form.get('mission', ''),
            vision=request.form.get('vision', ''),
            status=request.form.get('status', 'active'),
            published='published' in request.form,
            contact_email=request.form.get('contact_email', ''),
            contact_phone=request.form.get('contact_phone', ''),
            address=request.form.get('address', ''),
            timezone=request.form.get('timezone', ''),
            tags=request.form.get('tags', ''),
            instagram=request.form.get('instagram', ''),
            linkedin=request.form.get('linkedin', ''),
            website=request.form.get('website', ''),
            latitude=try_float(request.form.get('latitude')),
            longitude=try_float(request.form.get('longitude')),
        )
        if 'logo' in request.files and request.files['logo'].filename:
            chapter.logo = save_upload(request.files['logo'], 'logos')
        if 'cover_image' in request.files and request.files['cover_image'].filename:
            chapter.cover_image = save_upload(request.files['cover_image'], 'covers')

        db.session.add(chapter)
        db.session.commit()
        flash(f'Chapter "{chapter.name}" created!', 'success')
        return redirect(url_for('admin.chapters'))

    return render_template('admin/chapter_form.html', chapter=None)


@admin.route('/admin/chapters/<int:chapter_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def chapter_edit(chapter_id):
    chapter = db.session.get(Chapter, chapter_id)
    if not chapter:
        flash('Chapter not found.', 'error')
        return redirect(url_for('admin.chapters'))

    if request.method == 'POST':
        chapter.name = request.form.get('name', chapter.name)
        chapter.city = request.form.get('city', chapter.city)
        chapter.description = request.form.get('description', '')
        chapter.about = request.form.get('about', '')
        chapter.mission = request.form.get('mission', '')
        chapter.vision = request.form.get('vision', '')
        chapter.objectives = request.form.get('objectives', '')
        chapter.status = request.form.get('status', 'active')
        chapter.published = 'published' in request.form
        chapter.contact_email = request.form.get('contact_email', '')
        chapter.contact_phone = request.form.get('contact_phone', '')
        chapter.address = request.form.get('address', '')
        chapter.timezone = request.form.get('timezone', '')
        chapter.tags = request.form.get('tags', '')
        chapter.google_maps = request.form.get('google_maps', '')
        chapter.instagram = request.form.get('instagram', '')
        chapter.linkedin = request.form.get('linkedin', '')
        chapter.discord = request.form.get('discord', '')
        chapter.website = request.form.get('website', '')
        try:
            chapter.latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
        except (ValueError, TypeError):
            chapter.latitude = None
        try:
            chapter.longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
        except (ValueError, TypeError):
            chapter.longitude = None

        if 'logo' in request.files and request.files['logo'].filename:
            chapter.logo = save_upload(request.files['logo'], 'logos')
        if 'cover_image' in request.files and request.files['cover_image'].filename:
            chapter.cover_image = save_upload(request.files['cover_image'], 'covers')

        db.session.commit()
        flash('Chapter updated!', 'success')
        return redirect(url_for('admin.chapters'))

    return render_template('admin/chapter_form.html', chapter=chapter)


@admin.route('/admin/chapters/<int:chapter_id>/delete', methods=['POST'])
@super_admin_required
def chapter_delete(chapter_id):
    delete_chapter_by_id(chapter_id)
    return redirect(url_for('admin.chapters'))


@admin.route('/admin/chapters/<int:chapter_id>/toggle', methods=['POST'])
@super_admin_required
def chapter_toggle(chapter_id):
    toggle_chapter_published(chapter_id)
    return redirect(url_for('admin.chapters'))


# -- Sponsor CRUD --


def _clean_website(url):
    url = (url or '').strip()
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


@admin.route('/admin/sponsors')
@super_admin_required
def sponsors():
    sponsors = Sponsor.query.order_by(Sponsor.display_order, Sponsor.name).all()
    return render_template('admin/sponsors.html', sponsors=sponsors)


@admin.route('/admin/sponsors/create', methods=['GET', 'POST'])
@super_admin_required
def sponsor_create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Sponsor name is required.', 'error')
            return render_template('admin/sponsor_form.html', sponsor=None)

        sponsor = Sponsor(
            name=name,
            website=_clean_website(request.form.get('website')),
            description=request.form.get('description', '').strip(),
            published='published' in request.form,
            display_order=request.form.get('display_order', 0, type=int) or 0,
        )
        if 'logo' in request.files and request.files['logo'].filename:
            logo_path = save_upload(request.files['logo'], 'sponsors')
            if logo_path:
                sponsor.logo = logo_path
            else:
                flash('Logo upload was rejected (invalid image or over 4MB). Sponsor saved without a logo.', 'warning')

        db.session.add(sponsor)
        db.session.commit()
        log_audit('create', 'sponsor', sponsor.id, sponsor.name)
        flash(f'Sponsor "{sponsor.name}" added!', 'success')
        return redirect(url_for('admin.sponsors'))

    return render_template('admin/sponsor_form.html', sponsor=None)


@admin.route('/admin/sponsors/<int:sponsor_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def sponsor_edit(sponsor_id):
    sponsor = db.session.get(Sponsor, sponsor_id)
    if not sponsor:
        flash('Sponsor not found.', 'error')
        return redirect(url_for('admin.sponsors'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Sponsor name is required.', 'error')
            return render_template('admin/sponsor_form.html', sponsor=sponsor)

        sponsor.name = name
        sponsor.website = _clean_website(request.form.get('website'))
        sponsor.description = request.form.get('description', '').strip()
        sponsor.published = 'published' in request.form
        sponsor.display_order = request.form.get('display_order', 0, type=int) or 0

        if 'logo' in request.files and request.files['logo'].filename:
            logo_path = save_upload(request.files['logo'], 'sponsors')
            if logo_path:
                if sponsor.logo:
                    delete_upload(sponsor.logo)
                sponsor.logo = logo_path
            else:
                flash('New logo was rejected (invalid image or over 4MB). Keeping the current logo.', 'warning')

        db.session.commit()
        log_audit('update', 'sponsor', sponsor.id, sponsor.name)
        flash('Sponsor updated!', 'success')
        return redirect(url_for('admin.sponsors'))

    return render_template('admin/sponsor_form.html', sponsor=sponsor)


@admin.route('/admin/sponsors/<int:sponsor_id>/delete', methods=['POST'])
@super_admin_required
def sponsor_delete(sponsor_id):
    sponsor = db.session.get(Sponsor, sponsor_id)
    if not sponsor:
        flash('Sponsor not found.', 'error')
    else:
        sponsor.delete_files()
        db.session.delete(sponsor)
        db.session.commit()
        log_audit('delete', 'sponsor', sponsor_id, sponsor.name)
        flash(f'Sponsor "{sponsor.name}" deleted.', 'info')
    return redirect(url_for('admin.sponsors'))


@admin.route('/admin/sponsors/<int:sponsor_id>/toggle', methods=['POST'])
@super_admin_required
def sponsor_toggle(sponsor_id):
    sponsor = db.session.get(Sponsor, sponsor_id)
    if sponsor:
        sponsor.published = not sponsor.published
        db.session.commit()
        flash(f'Sponsor "{sponsor.name}" {"published" if sponsor.published else "unpublished"}.', 'success')
    return redirect(url_for('admin.sponsors'))


# -- User management --


@admin.route('/admin/users')
@super_admin_required
def users():
    users = User.query.order_by(User.name).all()
    chapters = Chapter.query.order_by(Chapter.name).all()
    roles = Role.query.order_by(Role.name).all()
    chapter_map = {c.id: c.name for c in chapters}
    return render_template('admin/users.html', users=users, chapters=chapters, chapter_map=chapter_map, roles=roles)


@admin.route('/admin/users/create', methods=['POST'])
@super_admin_required
def user_create():
    user = create_user_from_form()
    if user:
        flash(f'User "{user.name}" created!', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/admin/users/<int:user_id>/edit', methods=['GET'])
@super_admin_required
def user_edit_page(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    chapters = Chapter.query.order_by(Chapter.name).all()
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin/user_edit.html', user=user, chapters=chapters, roles=roles)


@admin.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@super_admin_required
def user_edit(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    if not update_user_from_form(user):
        return redirect(url_for('admin.user_edit_page', user_id=user_id))
    flash('User updated!', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@super_admin_required
def user_delete(user_id):
    delete_user_by_id(user_id)
    return redirect(url_for('admin.users'))


# -- Legacy admin routes --


@admin.route('/admin/legacy')
@super_admin_required
def legacy():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin.html', events=events)


def _save_gallery(event):
    """Attach uploaded gallery photos (and captions) to an event."""
    files = request.files.getlist('gallery_images')
    captions = request.form.getlist('gallery_captions')
    for i, file in enumerate(files):
        if file and file.filename:
            path = save_upload(file, 'events/gallery')
            if path:
                caption = captions[i] if i < len(captions) else ''
                img = EventImage(event_id=event.id, image=path, caption=caption,
                                 display_order=event.images.count())
                db.session.add(img)


@admin.route('/admin/post/new', methods=['GET', 'POST'])
@super_admin_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return render_template('new_post.html')
        post = Event(
            chapter_id=None,
            title=title,
            content=request.form.get('content', ''),
            author=request.form.get('author', '').strip() or 'Admin',
            description=strip_tags(request.form.get('content', ''))[:300],
            date=datetime.utcnow().date(),
            status='published',
        )
        db.session.add(post)
        db.session.commit()
        _save_gallery(post)
        db.session.commit()
        flash('Post published!', 'success')
        return redirect(url_for('public.blog'))
    return render_template('new_post.html')


@admin.route('/admin/post/<int:event_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_post(event_id):
    post = db.session.get(Event, event_id)
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('admin.legacy'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return render_template('edit_post.html', post=post)
        post.title = title
        post.content = request.form.get('content', '')
        author = request.form.get('author', '').strip()
        if author:
            post.author = author
        if not post.description:
            post.description = strip_tags(post.content)[:300]
        _save_gallery(post)
        for key, value in request.form.items():
            if key.startswith('caption_'):
                try:
                    img_id = int(key.split('_', 1)[1])
                except (ValueError, IndexError):
                    continue
                img = db.session.get(EventImage, img_id)
                if img and img.event_id == post.id:
                    img.caption = value
        for img_id in request.form.getlist('remove_image'):
            try:
                img = db.session.get(EventImage, int(img_id))
            except (ValueError, TypeError):
                continue
            if img and img.event_id == post.id:
                img.delete_files()
                db.session.delete(img)
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('public.blog'))
    return render_template('edit_post.html', post=post)


@admin.route('/admin/post/<int:event_id>/delete', methods=['POST'])
@super_admin_required
def delete_post(event_id):
    post = db.session.get(Event, event_id)
    if post:
        post.delete_files()
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', 'success')
    return redirect(url_for('admin.legacy'))


@admin.route('/admin/event/new', methods=['GET', 'POST'])
@super_admin_required
def new_event():
    if request.method == 'POST':
        try:
            event_date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            event_date = datetime.utcnow().date()
        chapter_id = request.form.get('chapter_id', type=int) or None
        event = Event(
            chapter_id=chapter_id,
            title=request.form.get('title', '').strip() or 'Untitled Event',
            content=request.form.get('content', ''),
            author=request.form.get('author', '').strip() or 'Admin',
            description=request.form.get('description', '') or request.form.get('content', '')[:300],
            venue=request.form.get('venue', ''),
            address=request.form.get('address', ''),
            time=request.form.get('time', ''),
            date=event_date,
            status=request.form.get('status', 'published'),
            registration_link=request.form.get('registration_link', ''),
            contact_email=request.form.get('contact_email', ''),
        )
        try:
            event.max_participants = int(request.form['max_participants']) if request.form.get('max_participants') else None
        except (ValueError, TypeError):
            event.max_participants = None
        if 'banner' in request.files and request.files['banner'].filename:
            event.banner = save_upload(request.files['banner'], 'events')
        db.session.add(event)
        db.session.commit()
        _save_gallery(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin.legacy'))
    chapters = Chapter.query.order_by(Chapter.name).all()
    return render_template('new_event.html', event=None, chapters=chapters)


@admin.route('/admin/event/<int:event_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('admin.legacy'))
    if request.method == 'POST':
        event.title = request.form.get('title', '').strip() or event.title
        event.content = request.form.get('content', '')
        event.chapter_id = request.form.get('chapter_id', type=int) or None
        author = request.form.get('author', '').strip()
        if author:
            event.author = author
        event.description = request.form.get('description', '') or request.form.get('content', '')[:300]
        event.venue = request.form.get('venue', '')
        event.address = request.form.get('address', '')
        event.time = request.form.get('time', '')
        event.registration_link = request.form.get('registration_link', '')
        event.contact_email = request.form.get('contact_email', '')
        try:
            event.max_participants = int(request.form['max_participants']) if request.form.get('max_participants') else None
        except (ValueError, TypeError):
            event.max_participants = None
        try:
            event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        except (ValueError, KeyError, TypeError):
            pass
        event.status = request.form.get('status', event.status)
        if 'banner' in request.files and request.files['banner'].filename:
            event.banner = save_upload(request.files['banner'], 'events')
        _save_gallery(event)
        for key, value in request.form.items():
            if key.startswith('caption_'):
                try:
                    img_id = int(key.split('_', 1)[1])
                except (ValueError, IndexError):
                    continue
                img = db.session.get(EventImage, img_id)
                if img and img.event_id == event.id:
                    img.caption = value
        for img_id in request.form.getlist('remove_image'):
            try:
                img = db.session.get(EventImage, int(img_id))
            except (ValueError, TypeError):
                continue
            if img and img.event_id == event.id:
                img.delete_files()
                db.session.delete(img)
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin.legacy'))
    chapters = Chapter.query.order_by(Chapter.name).all()
    return render_template('edit_event.html', event=event, chapters=chapters)


@admin.route('/admin/event/<int:event_id>/delete', methods=['POST'])
@super_admin_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if event:
        event.delete_files()
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin.legacy'))


# -- Super admin application views --


@admin.route('/admin/applications')
@super_admin_required
def applications():
    apps = Application.query.order_by(Application.created_at.desc()).all()
    chapters = {c.id: c.name for c in Chapter.query.all()}
    # Group by chapter
    from collections import defaultdict
    grouped = defaultdict(list)
    for a in apps:
        grouped[a.chapter_id].append(a)
    return render_template('admin/applications.html', grouped=dict(grouped), chapters=chapters)


@admin.route('/admin/applications/<int:app_id>/status', methods=['POST'])
@super_admin_required
def application_status(app_id):
    app_record = db.session.get(Application, app_id)
    if not app_record:
        flash('Application not found.', 'error')
        return redirect(url_for('admin.applications'))
    app_record.status = request.form.get('status', 'pending')
    db.session.commit()
    flash('Application status updated.', 'success')
    return redirect(url_for('admin.applications'))


# -- Role Management --


@admin.route('/admin/roles')
@super_admin_required
def roles():
    from btg.models import PERMISSIONS
    all_roles = Role.query.order_by(Role.name).all()
    return render_template('admin/roles.html', roles=all_roles, permissions=PERMISSIONS)


@admin.route('/admin/roles/create', methods=['POST'])
@super_admin_required
def role_create():
    create_role_from_form()
    return redirect(url_for('admin.roles'))


@admin.route('/admin/roles/<int:role_id>/edit', methods=['POST'])
@super_admin_required
def role_edit(role_id):
    role = db.session.get(Role, role_id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('admin.roles'))
    update_role_from_form(role)
    return redirect(url_for('admin.roles'))


@admin.route('/admin/roles/<int:role_id>/delete', methods=['POST'])
@super_admin_required
def role_delete(role_id):
    delete_role_by_id(role_id)
    return redirect(url_for('admin.roles'))


# -- Analytics --


@admin.route('/admin/analytics')
@super_admin_required
def analytics():
    from btg.models import GalleryImage
    total_chapters = Chapter.query.count()
    total_users = User.query.count()
    total_members = TeamMember.query.count()
    total_events = Event.query.count()
    total_gallery = GalleryImage.query.count()
    total_apps = Application.query.count()

    users_by_role = {}
    for user in User.query.all():
        role_name = user.display_role_name
        users_by_role[role_name] = users_by_role.get(role_name, 0) + 1

    chapters_by_status = {}
    for ch in Chapter.query.all():
        chapters_by_status[ch.status] = chapters_by_status.get(ch.status, 0) + 1

    per_chapter = []
    for c in Chapter.query.order_by(Chapter.name).all():
        per_chapter.append({
            'name': c.name,
            'members': TeamMember.query.filter_by(chapter_id=c.id).count(),
            'events': Event.query.filter_by(chapter_id=c.id).count(),
            'gallery': GalleryImage.query.filter_by(chapter_id=c.id).count(),
            'applications': Application.query.filter_by(chapter_id=c.id).count(),
        })

    apps_by_status = {}
    for app in Application.query.all():
        apps_by_status[app.status] = apps_by_status.get(app.status, 0) + 1

    stats = {
        'total_chapters': total_chapters,
        'total_users': total_users,
        'total_members': total_members,
        'total_events': total_events,
        'total_gallery': total_gallery,
        'total_applications': total_apps,
        'users_by_role': users_by_role,
        'chapters_by_status': chapters_by_status,
        'per_chapter': per_chapter,
        'apps_by_status': apps_by_status,
    }
    return render_template('admin/analytics.html', stats=stats)


# -- Homepage Stats --


@admin.route('/admin/site-stats', methods=['GET', 'POST'])
@super_admin_required
def site_stats():
    stat = SiteStat.get()
    if request.method == 'POST':
        stat.kits_delivered = try_int(request.form.get('kits_delivered'))
        stat.student_chapters = try_int(request.form.get('student_chapters'))
        stat.students_reached = try_int(request.form.get('students_reached'))
        db.session.commit()
        log_audit('update', 'site_stats', stat.id, 'Homepage Stats')
        flash('Homepage stats updated!', 'success')
        return redirect(url_for('admin.site_stats'))
    return render_template('admin/site_stats.html', stat=stat)


# -- Audit Logs --


@admin.route('/admin/logs')
@super_admin_required
def logs():
    from btg.models import AuditLog
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/logs.html', logs=logs)


# -- Sessions --


@admin.route('/admin/sessions')
@super_admin_required
def sessions():
    from btg.models import UserSession
    page = request.args.get('page', 1, type=int)
    sessions_query = UserSession.query.order_by(UserSession.last_active.desc()).paginate(page=page, per_page=50)
    user_map = {u.id: u.name for u in User.query.all()}
    for s in sessions_query.items:
        s.user_name = user_map.get(s.user_id, 'Unknown')
    return render_template('admin/sessions.html', sessions=sessions_query)


# -- Curriculum CRUD --


@admin.route('/admin/curriculum')
@super_admin_required
def curriculum():
    items = Curriculum.query.order_by(Curriculum.display_order, Curriculum.title).all()
    return render_template('admin/curriculum.html', items=items)


@admin.route('/admin/curriculum/create', methods=['GET', 'POST'])
@super_admin_required
def curriculum_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return render_template('admin/curriculum_form.html', item=None)
        item = Curriculum(
            title=title,
            description=request.form.get('description', '').strip(),
            status=request.form.get('status', 'in_progress'),
            category=request.form.get('category', '').strip(),
            grade_level=request.form.get('grade_level', '').strip(),
            file_url=_clean_website(request.form.get('file_url')),
            published='published' in request.form,
            display_order=request.form.get('display_order', 0, type=int) or 0,
        )
        db.session.add(item)
        db.session.commit()
        log_audit('create', 'curriculum', item.id, item.title)
        flash(f'Curriculum "{item.title}" added!', 'success')
        return redirect(url_for('admin.curriculum'))
    return render_template('admin/curriculum_form.html', item=None)


@admin.route('/admin/curriculum/<int:item_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def curriculum_edit(item_id):
    item = db.session.get(Curriculum, item_id)
    if not item:
        flash('Curriculum not found.', 'error')
        return redirect(url_for('admin.curriculum'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return render_template('admin/curriculum_form.html', item=item)
        item.title = title
        item.description = request.form.get('description', '').strip()
        item.status = request.form.get('status', 'in_progress')
        item.category = request.form.get('category', '').strip()
        item.grade_level = request.form.get('grade_level', '').strip()
        item.file_url = _clean_website(request.form.get('file_url'))
        item.published = 'published' in request.form
        item.display_order = request.form.get('display_order', 0, type=int) or 0
        db.session.commit()
        log_audit('update', 'curriculum', item.id, item.title)
        flash('Curriculum updated!', 'success')
        return redirect(url_for('admin.curriculum'))
    return render_template('admin/curriculum_form.html', item=item)


@admin.route('/admin/curriculum/<int:item_id>/delete', methods=['POST'])
@super_admin_required
def curriculum_delete(item_id):
    item = db.session.get(Curriculum, item_id)
    if not item:
        flash('Curriculum not found.', 'error')
    else:
        title = item.title
        db.session.delete(item)
        db.session.commit()
        log_audit('delete', 'curriculum', item_id, title)
        flash(f'Curriculum "{title}" deleted.', 'info')
    return redirect(url_for('admin.curriculum'))


# -- Board of Advisors CRUD --


@admin.route('/admin/advisors')
@super_admin_required
def advisors():
    people = Advisor.query.order_by(Advisor.display_order, Advisor.name).all()
    return render_template('admin/advisors.html', advisors=people)


@admin.route('/admin/advisors/create', methods=['GET', 'POST'])
@super_admin_required
def advisor_create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'error')
            return render_template('admin/advisor_form.html', advisor=None)

        slug_base = slugify(name)
        slug = slug_base
        counter = 1
        while Advisor.query.filter_by(slug=slug).first():
            slug = f'{slug_base}-{counter}'
            counter += 1

        person = Advisor(
            slug=slug, name=name,
            title=request.form.get('title', '').strip(),
            bio=request.form.get('bio', '').strip(),
            published='published' in request.form,
            display_order=request.form.get('display_order', 0, type=int) or 0,
        )
        if 'avatar' in request.files and request.files['avatar'].filename:
            path = save_upload(request.files['avatar'], 'advisors')
            if path:
                person.avatar = path
            else:
                flash('Avatar upload was rejected (invalid image or over 4MB). Saved without a photo.', 'warning')
        db.session.add(person)
        db.session.commit()
        _save_initiatives(person)
        log_audit('create', 'advisor', person.id, person.name)
        flash(f'Advisor "{person.name}" added!', 'success')
        return redirect(url_for('admin.advisors'))
    return render_template('admin/advisor_form.html', advisor=None)


@admin.route('/admin/advisors/<int:advisor_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def advisor_edit(advisor_id):
    person = db.session.get(Advisor, advisor_id)
    if not person:
        flash('Advisor not found.', 'error')
        return redirect(url_for('admin.advisors'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'error')
            return render_template('admin/advisor_form.html', advisor=person)
        person.name = name
        person.title = request.form.get('title', '').strip()
        person.bio = request.form.get('bio', '').strip()
        person.published = 'published' in request.form
        person.display_order = request.form.get('display_order', 0, type=int) or 0
        if 'avatar' in request.files and request.files['avatar'].filename:
            path = save_upload(request.files['avatar'], 'advisors')
            if path:
                if person.avatar:
                    delete_upload(person.avatar)
                person.avatar = path
            else:
                flash('New avatar was rejected (invalid image or over 4MB). Keeping the current photo.', 'warning')
        _save_initiatives(person)
        db.session.commit()
        log_audit('update', 'advisor', person.id, person.name)
        flash('Advisor updated!', 'success')
        return redirect(url_for('admin.advisors'))
    return render_template('admin/advisor_form.html', advisor=person)


@admin.route('/admin/advisors/<int:advisor_id>/delete', methods=['POST'])
@super_admin_required
def advisor_delete(advisor_id):
    person = db.session.get(Advisor, advisor_id)
    if not person:
        flash('Advisor not found.', 'error')
    else:
        name = person.name
        person.delete_files()
        db.session.delete(person)
        db.session.commit()
        log_audit('delete', 'advisor', advisor_id, name)
        flash(f'Advisor "{name}" deleted.', 'info')
    return redirect(url_for('admin.advisors'))


def _save_initiatives(person):
    """Replace an advisor's initiatives with the rows submitted in the form."""
    names = request.form.getlist('initiative_name')
    roles = request.form.getlist('initiative_role')
    descs = request.form.getlist('initiative_desc')
    for existing in person.initiatives.all():
        db.session.delete(existing)
    order = 0
    for i, nm in enumerate(names):
        nm = (nm or '').strip()
        if not nm:
            continue
        order += 1
        db.session.add(AdvisorInitiative(
            advisor_id=person.id, name=nm,
            role=(roles[i] if i < len(roles) else '').strip(),
            description=(descs[i] if i < len(descs) else '').strip(),
            display_order=order,
        ))
    db.session.commit()


# -- Newsletter subscribers --


@admin.route('/admin/subscribers')
@super_admin_required
def subscribers():
    people = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return render_template('admin/subscribers.html', subscribers=people)
