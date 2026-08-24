"""Business logic shared between the /admin and /gokul007 super-admin panels.

Both panels expose overlapping user/chapter/role management. Routes in
admin.py and secret.py stay separate (different templates, different
URL prefixes) but delegate their mutations here instead of each keeping
its own copy.
"""
from flask import request, flash, session

from btg.extensions import db
from btg.models import User, Chapter, Role, AuditLog


def log_audit(action, entity_type, entity_id=None, entity_name='', details=''):
    user_id = session.get('user_id')
    user = db.session.get(User, user_id) if user_id else None
    entry = AuditLog(
        user_id=user_id,
        user_name=user.name if user else 'System',
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        details=details,
        ip_address=request.remote_addr or '',
    )
    db.session.add(entry)
    db.session.commit()


# -- Users --


def create_user_from_form():
    """Create a user from the current request's form data.

    Sets a flash message and returns None on validation failure;
    returns the new User on success.
    """
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '')
    role_id = request.form.get('role_id', type=int)
    chapter_id = request.form.get('chapter_id', type=int)

    if not name or not email or not password or not username:
        flash('Name, email, username, and password are required.', 'error')
        return None
    if User.query.filter_by(email=email).first():
        flash('Email already in use.', 'error')
        return None
    if User.query.filter_by(username=username).first():
        flash('Username already taken.', 'error')
        return None

    user = User(name=name, email=email, username=username, role_id=role_id, chapter_id=chapter_id)
    user.sync_role_string()
    user.set_password(password)
    user.must_change_password = True
    db.session.add(user)
    db.session.commit()
    return user


def update_user_from_form(user):
    """Update `user` from the current request's form data.

    Returns True on success. On a username conflict, sets a flash
    message, leaves `user` untouched, and returns False.
    """
    username = request.form.get('username', '').strip().lower()
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return False
        user.username = username

    user.name = request.form.get('name', user.name)
    user.email = request.form.get('email', user.email).strip().lower()
    user.role_id = request.form.get('role_id', type=int) or None
    user.sync_role_string()
    user.chapter_id = request.form.get('chapter_id', type=int)
    password = request.form.get('password', '')
    if password:
        user.set_password(password)
        user.must_change_password = True
    db.session.commit()
    return True


def delete_user_by_id(user_id):
    """Delete a user unless they're a super admin. Returns True if deleted."""
    user = db.session.get(User, user_id)
    if user and not user.is_super_admin:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'info')
        return True
    flash('Cannot delete super admin.', 'error')
    return False


# -- Chapters --


def delete_chapter_by_id(chapter_id):
    chapter = db.session.get(Chapter, chapter_id)
    if not chapter:
        flash('Chapter not found.', 'error')
        return
    chapter.delete_files()
    db.session.delete(chapter)
    db.session.commit()
    flash(f'Chapter "{chapter.name}" deleted.', 'info')


def toggle_chapter_published(chapter_id):
    chapter = db.session.get(Chapter, chapter_id)
    if chapter:
        chapter.published = not chapter.published
        db.session.commit()
        flash(f'Chapter "{chapter.name}" {"published" if chapter.published else "unpublished"}.', 'success')


# -- Roles --


def create_role_from_form():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    if not name:
        flash('Role name is required.', 'error')
        return None
    if Role.query.filter_by(name=name).first():
        flash('Role already exists.', 'error')
        return None

    selected = request.form.getlist('permissions')
    role = Role(name=name, description=description)
    role.set_permissions(selected)
    db.session.add(role)
    db.session.commit()
    log_audit('create', 'role', role.id, role.name)
    flash(f'Role "{name}" created!', 'success')
    return role


def update_role_from_form(role):
    role.name = request.form.get('name', role.name)
    role.description = request.form.get('description', '').strip()
    selected = request.form.getlist('permissions')
    role.set_permissions(selected)
    db.session.commit()
    log_audit('update', 'role', role.id, role.name)
    flash(f'Role "{role.name}" updated!', 'success')


def delete_role_by_id(role_id):
    role = db.session.get(Role, role_id)
    if not role:
        flash('Role not found.', 'error')
        return
    if role.is_system:
        flash('System roles cannot be deleted.', 'error')
        return
    # Reassign any users on this role before removing it, so no user is
    # left with a role_id pointing at a deleted row.
    User.query.filter_by(role_id=role.id).update({User.role_id: None})
    log_audit('delete', 'role', role.id, role.name)
    db.session.delete(role)
    db.session.commit()
    flash(f'Role "{role.name}" deleted.', 'info')
