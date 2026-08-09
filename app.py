from flask import Flask, redirect, session, url_for
from config import Config
from extensions import babel, csrf, db
from flask_migrate import Migrate
from flask_login import LoginManager

# ======================================
# IMPORT BLUEPRINTS
# ======================================
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.image import image_bp
from routes.audio import audio_bp
from routes.video import video_bp
from routes.history import history_bp
from routes.profile import profile_bp
from routes.settings import settings_bp
from routes.progress import progress_bp

# ======================================
# FIX: admin_bp import - agar nahi hai toh admin import karo
# ======================================
try:
    from routes.admin import admin_bp
except ImportError:
    from routes.admin import admin as admin_bp


def create_app():
    app = Flask(__name__)

    # ======================================
    # Load Configuration
    # ======================================
    app.config.from_object(Config)

    # ======================================
    # Initialize Database
    # ======================================
    db.init_app(app)

    # ======================================
    # CSRF protection on every POST form
    # ======================================
    csrf.init_app(app)
    
    # ======================================
    # Initialize Flask-Migrate
    # ======================================
    migrate = Migrate(app, db)

    # ======================================
    # Initialize Flask-Babel (translations)
    # ======================================
    def get_locale():
        return session.get("language", app.config.get("BABEL_DEFAULT_LOCALE", "en"))

    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_locale():
        return {"current_locale": get_locale()}

    # ======================================
    # Initialize Flask-Login
    # ======================================
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # ======================================
    # Create Tables
    # ======================================
    with app.app_context():
        import models
        import history
        import login_log
        db.create_all()

    # ======================================
    # ROOT ROUTE - Redirect to login
    # ======================================
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # ======================================
    # Register Blueprints
    # ======================================
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(admin_bp)

    # ======================================
    # Context Processor for Notifications
    # ======================================
    @app.context_processor
    def utility_processor():
        def get_notifications():
            return []  # Add your notification logic here
        return dict(get_notifications=get_notifications)

    # ======================================
    # Error Handlers
    # ======================================
    @app.errorhandler(404)
    def not_found(e):
        return "Page not found", 404

    @app.errorhandler(413)
    def too_large(e):
        limit = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return f"The uploaded file is too large. The limit is {limit} MB.", 413

    @app.errorhandler(500)
    def server_error(e):
        return "Internal server error", 500

    return app


# ======================================
# Create Flask App
# ======================================
app = create_app()


# ======================================
# Run Application
# ======================================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        threaded=True
    )