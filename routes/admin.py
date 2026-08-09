import secrets
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from extensions import db
from models import User
from history import History
from login_log import LoginLog

# ======================================
# BLUEPRINT - admin_bp naam se
# ======================================
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ======================================
# ADMIN CHECK DECORATOR
# ======================================
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session and "username" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        if session.get("role") != "admin" and session.get("role") != "Admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.dashboard"))

        return func(*args, **kwargs)
    return wrapper

# ======================================
# ADMIN DASHBOARD
# ======================================
@admin_bp.route("/")
@admin_required
def admin_dashboard():
    try:
        users_count = User.query.count()
    except:
        users_count = 0

    try:
        history_count = History.query.count()
    except:
        history_count = 0

    activities = []
    try:
        activities = History.query.order_by(
            History.id.desc()
        ).limit(10).all()
    except:
        pass

    return render_template(
        "admin/admin.html",
        users_count=users_count,
        image_count=history_count,
        history_count=history_count,
        activities=activities
    )

# ======================================
# ADMIN - VIEW ALL USERS
# ======================================
@admin_bp.route("/users")
@admin_required
def admin_users():
    try:
        users = User.query.all()
    except:
        users = []
    
    return render_template("admin/users.html", users=users)

# ======================================
# ADMIN - DELETE USER
# ======================================
@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f"User {user.username} deleted successfully!", "success")
        else:
            flash("User not found.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    
    return redirect(url_for("admin.admin_users"))

# ======================================
# ADMIN - PROMOTE USER
# ======================================
@admin_bp.route("/users/promote/<int:user_id>", methods=["POST"])
@admin_required
def admin_promote_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            user.role = "admin"
            db.session.commit()
            flash(f"User {user.username} promoted to admin!", "success")
        else:
            flash("User not found.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    
    return redirect(url_for("admin.admin_users"))

# ======================================
# ADMIN - SECURITY
# ======================================
@admin_bp.route("/security")
@admin_required
def admin_security():
    logs = []
    users = []
    stats = {
        "total": 0,
        "failed_24h": 0,
        "locked": 0,
        "last_failed": None
    }

    try:
        logs = LoginLog.query.order_by(LoginLog.id.desc()).limit(100).all()
    except Exception:
        pass

    try:
        users = User.query.order_by(User.username.asc()).all()
    except Exception:
        pass

    try:
        since = datetime.utcnow() - timedelta(hours=24)
        stats["total"] = LoginLog.query.count()
        stats["failed_24h"] = LoginLog.query.filter(
            LoginLog.status != "Success",
            LoginLog.created_at >= since
        ).count()
        stats["locked"] = User.query.filter_by(is_active=False).count()

        last_failed = LoginLog.query.filter(
            LoginLog.status != "Success"
        ).order_by(LoginLog.id.desc()).first()
        stats["last_failed"] = last_failed.created_at if last_failed else None
    except Exception:
        pass

    return render_template(
        "admin/security.html",
        logs=logs,
        users=users,
        stats=stats
    )


# ======================================
# ADMIN - LOCK / UNLOCK ACCOUNT
# ======================================
@admin_bp.route("/security/toggle-lock/<int:user_id>", methods=["POST"])
@admin_required
def admin_toggle_lock(user_id):
    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.admin_security"))

    if user.id == session.get("user_id"):
        flash("You cannot lock your own account.", "warning")
        return redirect(url_for("admin.admin_security"))

    try:
        user.is_active = not bool(user.is_active)
        db.session.commit()
        state = "unlocked" if user.is_active else "locked"
        flash(f"Account '{user.username}' has been {state}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin.admin_security"))


# ======================================
# ADMIN - FORCE PASSWORD RESET
# ======================================
@admin_bp.route("/security/reset-password/<int:user_id>", methods=["POST"])
@admin_required
def admin_reset_password(user_id):
    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.admin_security"))

    new_password = request.form.get("new_password", "").strip()

    if not new_password:
        alphabet = string.ascii_letters + string.digits
        new_password = "".join(secrets.choice(alphabet) for _ in range(12))
    elif len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.admin_security"))

    try:
        user.set_password(new_password)
        db.session.commit()
        flash(
            f"Password for '{user.username}' was reset to: {new_password} "
            "- share it with them and ask them to change it.",
            "success"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin.admin_security"))


# ======================================
# ADMIN - CLEAR LOGIN LOG
# ======================================
@admin_bp.route("/security/clear-logs", methods=["POST"])
@admin_required
def admin_clear_login_logs():
    try:
        deleted = LoginLog.query.delete()
        db.session.commit()
        flash(f"Cleared {deleted} login records.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin.admin_security"))


# ======================================
# ADMIN - HISTORY
# ======================================
@admin_bp.route("/history")
@admin_required
def admin_history():
    try:
        history = History.query.order_by(History.id.desc()).limit(50).all()
    except:
        history = []
    
    return render_template("admin/history.html", history=history)