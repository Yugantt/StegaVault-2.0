from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash
)
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import os

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

@settings_bp.route("/")
def settings():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("auth.login"))

    theme = session.get("theme", "light")
    notifications = session.get("notifications", True)
    language = session.get("language", "en")

    return render_template(
        "dashboard/settings.html",
        user=user,
        theme=theme,
        notifications=notifications,
        language=language
    )

@settings_bp.route("/update-profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    language = request.form.get("language")

    if full_name:
        user.full_name = full_name
    
    if email:
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("settings.settings"))
        user.email = email

    if language and language in Config.LANGUAGES:
        session["language"] = language

    db.session.commit()
    flash("Settings updated successfully!", "success")
    return redirect(url_for("settings.settings"))

@settings_bp.route("/theme", methods=["POST"])
def update_theme():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    theme = request.form.get("theme", "light")
    
    if theme not in ["light", "dark"]:
        flash("Invalid theme selection.", "danger")
        return redirect(url_for("settings.settings"))
    
    session["theme"] = theme
    flash(f"Theme updated to {theme} mode!", "success")
    
    return redirect(url_for("settings.settings"))

@settings_bp.route("/notifications", methods=["POST"])
def update_notifications():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    notifications = request.form.get("notifications") == "on"
    session["notifications"] = notifications
    
    flash("Notification preferences updated!", "success")
    return redirect(url_for("settings.settings"))

@settings_bp.route("/language", methods=["POST"])
def update_language():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    language = request.form.get("language", "en")
    
    if language not in Config.LANGUAGES:
        flash("Invalid language selection.", "danger")
        return redirect(url_for("settings.settings"))
    
    session["language"] = language
    flash(f"Language updated to {Config.LANGUAGES[language]}!", "success")
    
    return redirect(url_for("settings.settings"))

@settings_bp.route("/clear-data", methods=["POST"])
def clear_data():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    from history import History
    History.query.filter_by(user_id=user.id).delete()
    
    session.pop("theme", None)
    session.pop("notifications", None)
    session.pop("language", None)
    
    db.session.commit()
    
    flash("All data cleared successfully!", "success")
    return redirect(url_for("settings.settings"))

@settings_bp.route("/delete-account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    password = request.form.get("password")
    
    if not password:
        flash("Please enter your password to confirm.", "danger")
        return redirect(url_for("settings.settings"))
    
    if not check_password_hash(user.password, password):
        flash("Incorrect password.", "danger")
        return redirect(url_for("settings.settings"))

    from history import History
    History.query.filter_by(user_id=user.id).delete()
    
    if user.profile_image and user.profile_image != "default.png":
        profile_path = os.path.join(Config.PROFILE_FOLDER, user.profile_image)
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
            except:
                pass
    
    db.session.delete(user)
    db.session.commit()
    
    session.clear()
    flash("Account deleted successfully.", "info")
    return redirect(url_for("auth.login"))
