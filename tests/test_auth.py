"""Test authentication and role-based access."""


def test_public_pages(client):
    resp = client.get('/')
    assert resp.status_code == 200

    resp = client.get('/chapters')
    assert resp.status_code == 200

    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_success(client):
    resp = client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })
    assert resp.status_code == 302  # redirect to dashboard


def test_login_by_username(client):
    resp = client.post('/login', data={
        'email': 'arvind',
        'password': 'trial@123',
    })
    assert resp.status_code == 302  # redirect to dashboard


def test_login_failure(client):
    resp = client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'wrong-password',
    })
    assert resp.status_code == 200  # re-renders login page


def test_logout(client):
    client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })
    resp = client.post('/logout')
    assert resp.status_code == 302


def test_logout_requires_post(client):
    client.post('/login', data={
        'email': 'arvindtrial@gmail.com',
        'password': 'trial@123',
    })
    resp = client.get('/logout')
    assert resp.status_code == 405


def test_login_required_redirect(client):
    resp = client.get('/admin')
    assert resp.status_code == 302  # redirect to login


def test_gokul007_no_autologin(client):
    """Verify /gokul007 does not auto-login (security fix)."""
    resp = client.get('/gokul007')
    assert resp.status_code == 302  # redirect to login

    # Verify no session set
    resp = client.get('/gokul007/dashboard')
    assert resp.status_code == 302  # still redirects


def test_role_boundary_chapter_president(client):
    """Verify a chapter president cannot access another chapter's data."""
    from btg.extensions import db as _db
    from btg.models import User, Chapter

    # Create two chapters
    c1 = Chapter(slug='ch1', name='Chapter 1', city='City 1')
    c2 = Chapter(slug='ch2', name='Chapter 2', city='City 2')
    _db.session.add_all([c1, c2])
    _db.session.commit()

    # Create chapter president for ch1 only
    pres = User(
        name='Pres 1', email='pres1@test.com',
        role='chapter_president', chapter_id=c1.id,
        must_change_password=False,
    )
    pres.set_password('test1234')
    _db.session.add(pres)
    _db.session.commit()

    client.post('/login', data={
        'email': 'pres1@test.com',
        'password': 'test1234',
    })

    # Should be able to access ch1 dashboard
    resp = client.get('/dashboard')
    assert resp.status_code == 200

    # Should NOT be able to delete ch2 events via API
    resp = client.post(f'/dashboard/events/create', data={
        'chapter_id': c2.id,
        'title': 'Evil Event',
        'date': '2026-12-01',
    })
    # Should fail because chapter_id doesn't match user's chapter
    assert resp.status_code in (302,)  # redirected with error


def test_new_hashes_use_the_configured_memory_light_method(db):
    """Passwords must not be stored with scrypt.

    Werkzeug's scrypt default allocates ~33 MiB per hash *and per verify*.
    Several workers hashing at once was enough to put the box under memory
    pressure, and the resulting SIGTERM landed mid-`hashlib.scrypt` and
    restarted the service on what was often a user's very first login.
    """
    from btg.models import User

    user = User(name='Fresh', email='fresh@test.com', username='fresh')
    user.set_password('hunter2222')

    assert user.password_hash.startswith('pbkdf2:')
    assert 'scrypt' not in user.password_hash
    assert not user.needs_password_rehash


def test_legacy_scrypt_hash_is_upgraded_on_successful_login(client, db):
    """An account stored with the old method logs in, then stops using it."""
    from werkzeug.security import generate_password_hash
    from btg.models import User

    user = User(name='Legacy', email='legacy@test.com', username='legacy',
                role='super_admin', must_change_password=False)
    # cheap scrypt params: this asserts the upgrade path, not scrypt's cost
    user.password_hash = generate_password_hash('oldpass123', method='scrypt:1024:8:1')
    db.session.add(user)
    db.session.commit()
    assert user.needs_password_rehash

    resp = client.post('/login', data={'email': 'legacy', 'password': 'oldpass123'})
    assert resp.status_code == 302

    refreshed = User.query.filter_by(username='legacy').first()
    assert refreshed.password_hash.startswith('pbkdf2:')
    assert not refreshed.needs_password_rehash


def test_unreadable_password_hash_is_a_failed_login_not_a_crash(db):
    """A hash this OpenSSL build cannot compute must not raise into the view."""
    from btg.models import User

    user = User(name='Broken', email='broken@test.com', username='broken')
    for bad in ('', 'not-a-hash', 'nosuchmethod$abc$def', 'scrypt:99999999:8:1$s$ff'):
        user.password_hash = bad
        assert user.check_password('anything') is False


def test_set_password_leaves_the_forced_change_flag_to_the_caller(db):
    """Seeded accounts asked to change their password must keep that flag."""
    from btg.models import User

    user = User(name='Seeded', email='seeded@test.com', username='seeded',
                must_change_password=True)
    user.set_password('temp12345')
    assert user.must_change_password is True


def test_first_login_with_temporary_password_forces_a_change(client, db):
    from btg.models import User

    user = User(name='New Pres', email='newpres@test.com', username='newpres',
                role='chapter_president', must_change_password=True)
    user.set_password('temp12345')
    db.session.add(user)
    db.session.commit()

    resp = client.post('/login', data={'email': 'newpres', 'password': 'temp12345'})
    assert resp.status_code == 302
    assert '/change-password' in resp.headers['Location']

    resp = client.post('/change-password', data={
        'current_password': 'temp12345',
        'new_password': 'brandnew123',
        'confirm_password': 'brandnew123',
    })
    assert resp.status_code == 302
    assert User.query.filter_by(username='newpres').first().must_change_password is False
