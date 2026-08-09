from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash
)
from extensions import db
from history import History

# ======================================
# BLUEPRINT - URL PREFIX ADD KIYA
# ======================================
history_bp = Blueprint(
    "history",
    __name__,
    url_prefix="/history"
)

# ======================================
# HISTORY PAGE
# ======================================
@history_bp.route("/")
def history_page():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    username = session.get("username")
    search = request.args.get("search", "").strip()

    query = History.query.filter_by(username=username)

    if search:
        query = query.filter(
            History.filename.ilike(f"%{search}%")
        )

    records = (
        query
        .order_by(History.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard/history.html",
        records=records,
        search=search
    )

# ======================================
# DELETE HISTORY
# ======================================
@history_bp.route("/delete/<int:id>", methods=["POST"])
def delete_history(id):
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    username = session.get("username")

    record = History.query.filter_by(
        id=id,
        username=username
    ).first()

    if record is None:
        flash("History record not found.", "danger")
        return redirect(url_for("history.history_page"))

    db.session.delete(record)
    db.session.commit()

    flash("History deleted successfully.", "success")
    return redirect(url_for("history.history_page"))

# ======================================
# CLEAR HISTORY
# ======================================
@history_bp.route("/clear", methods=["POST"])
def clear_history():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    username = session.get("username")

    deleted = (
        History.query
        .filter_by(username=username)
        .delete()
    )

    db.session.commit()

    if deleted > 0:
        flash("History cleared successfully.", "success")
    else:
        flash("No history available.", "info")

    return redirect(url_for("history.history_page"))