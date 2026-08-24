"""Test homepage stats admin editing and public display."""
from btg.models import SiteStat


def _login_admin(client):
    client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })


def test_site_stats_page_requires_admin(client):
    resp = client.get('/admin/site-stats')
    assert resp.status_code == 302  # redirected to login


def test_home_shows_placeholder_when_unset(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.data.count(b'>--<') >= 3


def test_site_stats_update_reflects_on_home(client):
    _login_admin(client)
    resp = client.post('/admin/site-stats', data={
        'kits_delivered': '42',
        'student_chapters': '5',
        'students_reached': '1200',
    })
    assert resp.status_code == 302

    stat = SiteStat.query.first()
    assert stat.kits_delivered == 42
    assert stat.student_chapters == 5
    assert stat.students_reached == 1200

    resp = client.get('/')
    assert b'42' in resp.data
    assert b'1200' in resp.data


def test_site_stats_blank_field_falls_back_to_placeholder(client):
    _login_admin(client)
    client.post('/admin/site-stats', data={
        'kits_delivered': '10',
        'student_chapters': '',
        'students_reached': '20',
    })
    stat = SiteStat.query.first()
    assert stat.kits_delivered == 10
    assert stat.student_chapters is None
    assert stat.students_reached == 20

    resp = client.get('/')
    assert resp.data.count(b'>--<') >= 1
