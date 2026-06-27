import os
import logging
from flask import Flask, session, render_template
from datetime import datetime

from btg.config import Config, BASE_DIR
from btg.extensions import db, csrf, migrate
from btg.models import User, Chapter, Event, EventImage, TeamMember, GalleryImage, Announcement, Application
from btg.blueprints.public import public
from btg.blueprints.auth_bp import auth
from btg.blueprints.admin import admin
from btg.blueprints.dashboard import dashboard
from btg.blueprints.secret import secret


def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Ensure upload directories exist
    for sub in ['logos', 'covers', 'team', 'events', 'events/gallery', 'gallery']:
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, sub), exist_ok=True)

    # Ensure data directory exists
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

    # Register blueprints
    app.register_blueprint(public)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(dashboard)
    app.register_blueprint(secret)

    # Context processors
    @app.context_processor
    def inject_user():
        user = None
        if session.get('user_id'):
            user = db.session.get(User, session['user_id'])
        return {'current_user': user}

    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    # Healthcheck
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    # Logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Initialize database
    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    """Seed admin user and sample chapters if DB is empty."""
    admin = User.query.filter_by(role='super_admin').first()
    if not admin:
        admin_email = Config.SEED_ADMIN_EMAIL
        admin_pw = Config.SEED_ADMIN_PASSWORD or 'btg-admin-2026'
        admin = User(
            name='Admin',
            email=admin_email,
            role='super_admin',
            must_change_password=False,
        )
        admin.set_password(admin_pw)
        db.session.add(admin)

    if Chapter.query.count() == 0:
        samples = [
            {
                'slug': 'chennai', 'name': 'Chennai Chapter',
                'city': 'Chennai',
                'description': 'Bringing robotics to students in Chennai.',
                'about': 'Our Chennai chapter runs weekly robotics workshops.',
                'mission': 'Make STEM accessible to every child in Chennai.',
                'status': 'active',
                'latitude': 13.0827, 'longitude': 80.2707,
            },
            {
                'slug': 'bangalore', 'name': 'Bangalore Chapter',
                'city': 'Bangalore',
                'description': 'Inspiring young innovators in Bangalore.',
                'about': 'Bangalore chapter focuses on kit distribution.',
                'mission': 'Build the next generation of innovators.',
                'status': 'active',
                'latitude': 12.9716, 'longitude': 77.5946,
            },
        ]
        for s in samples:
            c = Chapter(**s)
            db.session.add(c)
        db.session.commit()

        pres_pw = Config.SEED_PRESIDENT_PASSWORD or 'btg-chennai-2026'
        pres = User.query.filter_by(role='chapter_president').first()
        if not pres:
            pres = User(
                name='Chennai President',
                email='president.chennai@bridgethegaprobotics.org',
                role='chapter_president',
                chapter_id=Chapter.query.filter_by(slug='chennai').first().id,
                must_change_password=True,
            )
            pres.set_password(pres_pw)
            db.session.add(pres)

        pres_pw2 = Config.SEED_PRESIDENT_PASSWORD or 'btg-bangalore-2026'
        pres2 = User(
            name='Bangalore President',
            email='president.bangalore@bridgethegaprobotics.org',
            role='chapter_president',
            chapter_id=Chapter.query.filter_by(slug='bangalore').first().id,
            must_change_password=True,
        )
        pres2.set_password(pres_pw2)
        db.session.add(pres2)

    db.session.commit()
