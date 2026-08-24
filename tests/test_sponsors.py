"""Test sponsor admin CRUD and public display."""
import io

from btg.models import Sponsor
from btg.extensions import db as _db


def _login_admin(client):
    client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })


def test_sponsors_page_requires_admin(client):
    resp = client.get('/admin/sponsors')
    assert resp.status_code == 302  # redirected to login


def test_sponsor_create_and_list(client):
    _login_admin(client)
    resp = client.post('/admin/sponsors/create', data={
        'name': 'Acme Robotics',
        'website': 'acme.example.com',
        'description': 'Kit sponsor',
        'published': 'on',
        'display_order': '2',
    }, content_type='multipart/form-data')
    assert resp.status_code == 302

    sponsor = Sponsor.query.filter_by(name='Acme Robotics').first()
    assert sponsor is not None
    # scheme auto-prefixed
    assert sponsor.website == 'https://acme.example.com'
    assert sponsor.published is True
    assert sponsor.display_order == 2

    resp = client.get('/admin/sponsors')
    assert resp.status_code == 200
    assert b'Acme Robotics' in resp.data


def test_sponsor_create_requires_name(client):
    _login_admin(client)
    resp = client.post('/admin/sponsors/create', data={
        'name': '   ',
    }, content_type='multipart/form-data')
    assert resp.status_code == 200  # re-renders form
    assert Sponsor.query.count() == 0


def test_sponsor_edit(client):
    _login_admin(client)
    sponsor = Sponsor(name='Old Name')
    _db.session.add(sponsor)
    _db.session.commit()

    resp = client.post(f'/admin/sponsors/{sponsor.id}/edit', data={
        'name': 'New Name',
        'website': '',
        'description': 'updated',
        'display_order': '5',
    }, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert sponsor.name == 'New Name'
    assert sponsor.description == 'updated'
    assert sponsor.display_order == 5
    # checkbox absent -> unpublished
    assert sponsor.published is False


def test_sponsor_toggle_and_public_visibility(client):
    _login_admin(client)
    sponsor = Sponsor(name='Visible Sponsor', published=True)
    _db.session.add(sponsor)
    _db.session.commit()

    resp = client.get('/partners')
    assert b'Visible Sponsor' in resp.data

    # follow the redirect so the flash message (which contains the name) is consumed
    resp = client.post(f'/admin/sponsors/{sponsor.id}/toggle', follow_redirects=True)
    assert resp.status_code == 200
    assert sponsor.published is False

    resp = client.get('/partners')
    assert b'Visible Sponsor' not in resp.data


def test_sponsor_delete(client):
    _login_admin(client)
    sponsor = Sponsor(name='Doomed Sponsor')
    _db.session.add(sponsor)
    _db.session.commit()
    sid = sponsor.id

    resp = client.post(f'/admin/sponsors/{sid}/delete')
    assert resp.status_code == 302
    assert _db.session.get(Sponsor, sid) is None


def test_sponsor_missing_returns_redirect(client):
    _login_admin(client)
    resp = client.get('/admin/sponsors/99999/edit')
    assert resp.status_code == 302
    resp = client.post('/admin/sponsors/99999/delete')
    assert resp.status_code == 302
    resp = client.post('/admin/sponsors/99999/toggle')
    assert resp.status_code == 302


def test_partners_page_without_sponsors(client):
    resp = client.get('/partners')
    assert resp.status_code == 200
    # sponsor section hidden entirely when none exist
    assert b'Our Sponsors' not in resp.data


def test_invalid_logo_upload_rejected_gracefully(client):
    _login_admin(client)
    resp = client.post('/admin/sponsors/create', data={
        'name': 'Bad Logo Co',
        'logo': (io.BytesIO(b'not-an-image-at-all-plus-padding'), 'evil.png'),
    }, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200
    sponsor = Sponsor.query.filter_by(name='Bad Logo Co').first()
    assert sponsor is not None
    assert sponsor.logo == ''  # rejected upload leaves no logo
