import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from btg.config import Config
from btg.extensions import db
from btg.services.upload import delete_upload

# The method prefix Werkzeug actually writes for Config.PASSWORD_HASH_METHOD.
# Werkzeug fills in its own defaults (a bare 'pbkdf2' is stored as
# 'pbkdf2:sha256:1000000'), so comparing a stored hash against the raw config
# string would mark every freshly written hash as stale and re-hash on every
# single login. Derived once per process, on first use.
_current_hash_prefix = None


def _hash_prefix():
    global _current_hash_prefix
    if _current_hash_prefix is None:
        _current_hash_prefix = generate_password_hash(
            'prefix-probe', method=Config.PASSWORD_HASH_METHOD, salt_length=1
        ).split('$', 1)[0]
    return _current_hash_prefix


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(60), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='chapter_president')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    must_change_password = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    custom_role = db.relationship('Role', backref='users', lazy=True)

    @property
    def is_super_admin(self):
        if self.custom_role and self.custom_role.name == 'Super Admin':
            return True
        return self.role == 'super_admin'

    @property
    def display_role_name(self):
        if self.custom_role:
            return self.custom_role.name
        return self.role.replace('_', ' ').title()

    def sync_role_string(self):
        if self.custom_role:
            self.role = self.custom_role.name.lower().replace(' ', '_')

    def set_password(self, password):
        """Store `password` using the configured hash method.

        Deliberately does not touch `must_change_password`: whether a new
        password clears the forced-change flag depends on who set it (the
        owner clears it, an admin issuing a temporary one does not), so every
        caller states its own intent.
        """
        self.password_hash = generate_password_hash(
            password, method=Config.PASSWORD_HASH_METHOD
        )

    @property
    def needs_password_rehash(self):
        """True when the stored hash predates the configured method."""
        if not self.password_hash:
            return False
        return self.password_hash.split('$', 1)[0] != _hash_prefix()

    def check_password(self, password):
        """Verify `password`, upgrading a legacy hash on the way through.

        A hash written by an older method (scrypt, before the switch to
        pbkdf2) still verifies, and is rewritten in place on success so the
        expensive method is used at most once more per account. The caller is
        responsible for committing the session.
        """
        if not self.password_hash:
            return False
        try:
            matched = check_password_hash(self.password_hash, password)
        except (ValueError, MemoryError):
            # A stored hash this build of OpenSSL cannot compute (unknown
            # method, or scrypt over its memory limit) is a failed login,
            # not a 500 that takes the request down with it.
            return False
        if matched and self.needs_password_rehash:
            self.set_password(password)
        return matched


# Predefined permission flags
PERMISSIONS = [
    ('manage_users', 'Manage Users'),
    ('manage_chapters', 'Manage Chapters'),
    ('manage_events', 'Manage Events'),
    ('manage_announcements', 'Manage Announcements'),
    ('manage_applications', 'Manage Applications'),
    ('manage_roles', 'Manage Roles'),
    ('view_analytics', 'View Analytics'),
]


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    permissions = db.Column(db.Text, default='[]')
    is_system = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_permissions(self):
        return json.loads(self.permissions) if self.permissions else []

    def set_permissions(self, perms_list):
        self.permissions = json.dumps(perms_list)

    def has_permission(self, perm):
        return perm in self.get_permissions()


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    about = db.Column(db.Text, default='')
    mission = db.Column(db.Text, default='')
    vision = db.Column(db.Text, default='')
    objectives = db.Column(db.Text, default='')
    cover_image = db.Column(db.String(500), default='')
    logo = db.Column(db.String(500), default='')
    status = db.Column(db.String(20), default='active')
    published = db.Column(db.Boolean, default=True)
    contact_email = db.Column(db.String(120), default='')
    contact_phone = db.Column(db.String(50), default='')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(500), default='')
    timezone = db.Column(db.String(20), default='')
    tags = db.Column(db.String(300), default='')
    google_maps = db.Column(db.String(500), default='')
    instagram = db.Column(db.String(500), default='')
    linkedin = db.Column(db.String(500), default='')
    discord = db.Column(db.String(500), default='')
    website = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship('TeamMember', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    gallery = db.relationship('GalleryImage', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')

    def delete_files(self):
        delete_upload(self.cover_image)
        delete_upload(self.logo)

    def __repr__(self):
        return f'<Chapter {self.name}>'


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, default='')
    photo = db.Column(db.String(500), default='')
    linkedin = db.Column(db.String(500), default='')
    email = db.Column(db.String(120), default='')
    display_order = db.Column(db.Integer, default=0)

    def delete_files(self):
        delete_upload(self.photo)


class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    logo = db.Column(db.String(500), default='')
    website = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    published = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def delete_files(self):
        delete_upload(self.logo)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    content = db.Column(db.Text, default='')
    author = db.Column(db.String(120), default='Admin')
    venue = db.Column(db.String(300), default='')
    address = db.Column(db.String(500), default='')
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), default='')
    status = db.Column(db.String(20), default='upcoming')
    registration_link = db.Column(db.String(500), default='')
    contact_email = db.Column(db.String(120), default='')
    max_participants = db.Column(db.Integer, nullable=True)
    banner = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('EventImage', backref='event', lazy='dynamic', cascade='all, delete-orphan')

    def delete_files(self):
        delete_upload(self.banner)
        for img in self.images:
            img.delete_files()


class EventImage(db.Model):
    __tablename__ = 'event_images'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(300), default='')
    display_order = db.Column(db.Integer, default=0)

    def delete_files(self):
        delete_upload(self.image)


class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(300), default='')
    display_order = db.Column(db.Integer, default=0)

    def delete_files(self):
        delete_upload(self.image)


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    applicant_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    school = db.Column(db.String(200), default='')
    city = db.Column(db.String(120), default='')
    interests = db.Column(db.Text, default='')
    motivation = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_name = db.Column(db.String(120), default='System')
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    entity_name = db.Column(db.String(200), default='')
    details = db.Column(db.Text, default='')
    ip_address = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs', lazy=True)


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(256), unique=True, nullable=False)
    ip_address = db.Column(db.String(50), default='')
    user_agent = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='sessions', lazy=True)


class SiteStat(db.Model):
    __tablename__ = 'site_stats'
    id = db.Column(db.Integer, primary_key=True)
    kits_delivered = db.Column(db.Integer, nullable=True)
    student_chapters = db.Column(db.Integer, nullable=True)
    students_reached = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get():
        stat = SiteStat.query.first()
        if not stat:
            stat = SiteStat()
            db.session.add(stat)
            db.session.commit()
        return stat


class Curriculum(db.Model):
    __tablename__ = 'curricula'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='in_progress')  # complete | in_progress
    category = db.Column(db.String(120), default='')
    grade_level = db.Column(db.String(60), default='')
    file_url = db.Column(db.String(500), default='')
    published = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Curriculum {self.title}>'


class Advisor(db.Model):
    __tablename__ = 'advisors'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), default='')
    avatar = db.Column(db.String(500), default='')
    bio = db.Column(db.Text, default='')
    published = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    initiatives = db.relationship('AdvisorInitiative', backref='advisor',
                                  lazy='dynamic', cascade='all, delete-orphan')

    def delete_files(self):
        delete_upload(self.avatar)

    def __repr__(self):
        return f'<Advisor {self.name}>'


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    source = db.Column(db.String(60), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subscriber {self.email}>'


class AdvisorInitiative(db.Model):
    __tablename__ = 'advisor_initiatives'
    id = db.Column(db.Integer, primary_key=True)
    advisor_id = db.Column(db.Integer, db.ForeignKey('advisors.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(120), default='')
    description = db.Column(db.Text, default='')
    display_order = db.Column(db.Integer, default=0)
