"""Tests for the event management pipeline and blog routes."""
from datetime import date
from io import BytesIO

from PIL import Image

from btg.extensions import db as _db
from btg.models import User, Chapter, Event, EventImage


def _login(client):
    return client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })


def _png_bytes():
    buf = BytesIO()
    Image.new('RGB', (2, 2), color='red').save(buf, format='PNG')
    buf.seek(0)
    return buf


def _make_chapter():
    c = Chapter(slug='testch', name='Test Chapter', city='Test City')
    _db.session.add(c)
    _db.session.commit()
    return c


def test_blog_list_and_post(client):
    post = Event(
        chapter_id=None, title='Hello Blog', author='Admin',
        content='<p>Test post</p>', date=date(2026, 1, 1),
        status='published',
    )
    _db.session.add(post)
    _db.session.commit()

    resp = client.get('/blog')
    assert resp.status_code == 200
    assert b'Hello Blog' in resp.data

    resp = client.get(f'/blog/{post.id}')
    assert resp.status_code == 200
    assert b'Test post' in resp.data


def test_blog_hides_chapter_events(client):
    c = _make_chapter()
    ev = Event(chapter_id=c.id, title='Chapter Event', status='upcoming',
               date=date(2026, 1, 1))
    _db.session.add(ev)
    _db.session.commit()

    resp = client.get('/blog')
    assert b'Chapter Event' not in resp.data

    resp = client.get(f'/blog/{ev.id}')
    assert resp.status_code == 404


def test_event_create_with_gallery_and_captions(client):
    _login(client)
    c = _make_chapter()
    resp = client.post('/dashboard/events/create', data={
        'chapter_id': c.id,
        'title': 'Summer Camp',
        'date': '2026-07-20',
        'time': '10:00 AM',
        'venue': 'Test Hall',
        'address': '123 Main St, Chennai',
        'status': 'upcoming',
        'registration_link': 'https://example.com/reg',
        'contact_email': 'organizer@example.com',
        'max_participants': '50',
        'author': 'Arvind',
        'description': 'A fun camp',
        'content': '<p>Hands-on robots</p>',
        'gallery_images': [(_png_bytes(), 'a.png')],
        'gallery_captions': ['The workshop in action'],
    }, content_type='multipart/form-data')
    assert resp.status_code == 302

    ev = Event.query.filter_by(title='Summer Camp').first()
    assert ev is not None
    assert ev.address == '123 Main St, Chennai'
    assert ev.contact_email == 'organizer@example.com'
    assert ev.max_participants == 50
    assert ev.author == 'Arvind'
    assert ev.images.count() == 1
    img = ev.images.first()
    assert img.caption == 'The workshop in action'
    assert img.image.startswith('uploads/events/gallery/')


def test_event_update_caption_and_remove(client):
    _login(client)
    c = _make_chapter()
    client.post('/dashboard/events/create', data={
        'chapter_id': c.id,
        'title': 'Workshop',
        'date': '2026-08-01',
        'status': 'upcoming',
        'gallery_images': [(_png_bytes(), 'w.png')],
        'gallery_captions': ['First'],
    }, content_type='multipart/form-data')
    ev = Event.query.filter_by(title='Workshop').first()
    img = ev.images.first()

    resp = client.post('/dashboard/events/update', data={
        'event_id': ev.id,
        'title': 'Workshop 2',
        'date': '2026-08-02',
        'status': 'completed',
        'description': 'Updated',
        f'caption_{img.id}': 'Updated caption',
        'remove_image': str(img.id),
    })
    assert resp.status_code == 302

    _db.session.expire_all()
    assert _db.session.get(Event, ev.id).title == 'Workshop 2'
    assert _db.session.get(Event, ev.id).images.count() == 0


def test_event_create_validation(client):
    _login(client)
    c = _make_chapter()
    resp = client.post('/dashboard/events/create', data={
        'chapter_id': c.id,
        'title': '',
        'date': 'not-a-date',
    })
    assert resp.status_code == 302
    assert Event.query.count() == 0


def test_event_delete_cleans_gallery(client):
    _login(client)
    c = _make_chapter()
    client.post('/dashboard/events/create', data={
        'chapter_id': c.id,
        'title': 'To Delete',
        'date': '2026-09-01',
        'status': 'upcoming',
        'gallery_images': [(_png_bytes(), 'd.png')],
        'gallery_captions': ['Bye'],
    }, content_type='multipart/form-data')
    ev = Event.query.filter_by(title='To Delete').first()
    assert ev.images.count() == 1

    resp = client.post(f'/dashboard/events/{ev.id}/delete')
    assert resp.status_code == 302
    assert _db.session.get(Event, ev.id) is None
    assert EventImage.query.filter_by(event_id=ev.id).count() == 0


def test_admin_blog_post_lifecycle(client):
    _login(client)
    resp = client.post('/admin/post/new', data={
        'title': 'First Post',
        'author': 'Arvind',
        'content': '<p>Welcome</p>',
        'gallery_images': [(_png_bytes(), 'p.png')],
        'gallery_captions': ['Cover'],
    }, content_type='multipart/form-data')
    assert resp.status_code == 302

    post = Event.query.filter_by(title='First Post').first()
    assert post is not None
    assert post.chapter_id is None
    assert post.images.count() == 1

    resp = client.post(f'/admin/post/{post.id}/edit', data={
        'title': 'First Post v2',
        'author': 'Arvind',
        'content': '<p>Updated</p>',
        f'caption_{post.images.first().id}': 'New cap',
    })
    assert resp.status_code == 302
    _db.session.expire_all()
    assert _db.session.get(Event, post.id).title == 'First Post v2'

    resp = client.post(f'/admin/post/{post.id}/delete')
    assert resp.status_code == 302
    assert _db.session.get(Event, post.id) is None


def test_admin_event_lifecycle(client):
    _login(client)
    c = _make_chapter()
    resp = client.post('/admin/event/new', data={
        'chapter_id': c.id,
        'title': 'Legacy Event',
        'date': '2026-10-10',
        'time': '9:00 AM',
        'venue': 'Auditorium',
        'address': 'Downtown',
        'status': 'upcoming',
        'max_participants': '100',
        'contact_email': 'legacy@example.com',
        'gallery_images': [(_png_bytes(), 'l.png')],
        'gallery_captions': ['Legacy shot'],
    }, content_type='multipart/form-data')
    assert resp.status_code == 302

    ev = Event.query.filter_by(title='Legacy Event').first()
    assert ev is not None
    assert ev.chapter_id == c.id
    assert ev.max_participants == 100
    assert ev.images.count() == 1

    resp = client.post(f'/admin/event/{ev.id}/delete')
    assert resp.status_code == 302
    assert _db.session.get(Event, ev.id) is None
