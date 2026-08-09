from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    flash
)
from history import History

# ======================================
# BLUEPRINT - URL PREFIX ADD KIYA
# ======================================
dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

# ======================================
# USER DASHBOARD
# ======================================
@dashboard_bp.route("/")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    username = session.get("username")
    role = session.get("role")

    
    if role in ("admin", "Admin"):
        return redirect(url_for("admin.admin_dashboard"))

    stats = {
        "images_encoded": History.query.filter_by(
            username=username,
            module="Image",
            action="Encode"
        ).count(),

        "images_decoded": History.query.filter_by(
            username=username,
            module="Image",
            action="Decode"
        ).count(),

        "audio_files": History.query.filter_by(
            username=username,
            module="Audio"
        ).count(),

        "video_files": History.query.filter_by(
            username=username,
            module="Video"
        ).count()
    }

    history_records = (
        History.query
        .filter_by(username=username)
        .order_by(History.created_at.desc())
        .limit(5)
        .all()
    )

    activities = []
    for record in history_records:
        activities.append({
            "icon": "fa-lock" if record.action == "Encode" else "fa-unlock",
            "title": f"{record.module} {record.action} - {record.filename}",
            "time": record.created_at.strftime("%d %b %Y %I:%M %p")
        })

    notifications = [
        "Welcome to StegaVault 3.0",
        "Your data is protected using LSB Steganography.",
        "System running normally."
    ]

    return render_template(
        "dashboard/dashboard.html",
        username=username,
        role=role,
        stats=stats,
        notifications=notifications,
        activities=activities
    )