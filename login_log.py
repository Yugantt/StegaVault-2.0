from datetime import datetime

from extensions import db


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    # ==========================
    # PRIMARY KEY
    # ==========================
    id = db.Column(db.Integer, primary_key=True)

    # ==========================
    # WHO (user_id is null when the email is unknown)
    # ==========================
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    username = db.Column(db.String(100), nullable=True)

    # ==========================
    # RESULT: Success / Failed
    # ==========================
    status = db.Column(db.String(20), nullable=False, index=True)

    # ==========================
    # WHY IT FAILED
    # ==========================
    reason = db.Column(db.String(120), nullable=True)

    # ==========================
    # WHERE FROM
    # ==========================
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    # ==========================
    # WHEN
    # ==========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # ==========================
    # STRING
    # ==========================
    def __repr__(self):
        return f"<LoginLog {self.email} {self.status}>"


def record_login(request, status, email, user=None, reason=None):
    """
    Write one login attempt to the log. Never raises - a logging
    failure must not stop a user from logging in.
    """
    try:
        entry = LoginLog(
            user_id=user.id if user else None,
            email=email or "",
            username=user.username if user else None,
            status=status,
            reason=reason,
            ip_address=request.remote_addr,
            user_agent=(request.headers.get("User-Agent") or "")[:255]
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
