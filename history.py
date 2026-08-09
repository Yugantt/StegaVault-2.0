from extensions import db
from datetime import datetime


class History(db.Model):
    __tablename__ = "history"

    # ==========================
    # PRIMARY KEY
    # ==========================
    id = db.Column(db.Integer, primary_key=True)

    # ==========================
    # FOREIGN KEY
    # ==========================
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # ==========================
    # USER
    # ==========================
    username = db.Column(db.String(100), nullable=False, index=True)

    # ==========================
    # MODULE
    # ==========================
    module = db.Column(db.String(20), nullable=False, index=True)

    # ==========================
    # ACTION
    # ==========================
    action = db.Column(db.String(20), nullable=False, index=True)

    # ==========================
    # ORIGINAL FILE
    # ==========================
    filename = db.Column(db.String(255), nullable=False)

    # ==========================
    # OUTPUT FILE
    # ==========================
    output_filename = db.Column(db.String(255), nullable=True)

    # ==========================
    # SECRET MESSAGE
    # ==========================
    message = db.Column(db.Text, nullable=True)

    # ==========================
    # MESSAGE LENGTH
    # ==========================
    message_length = db.Column(db.Integer, default=0)

    # ==========================
    # FILE SIZE
    # ==========================
    file_size = db.Column(db.Integer, default=0)

    # ==========================
    # PROCESSING TIME
    # ==========================
    processing_time = db.Column(db.Float, default=0.0)

    # ==========================
    # STATUS
    # ==========================
    status = db.Column(db.String(20), default="Success")

    # ==========================
    # CREATED TIME
    # ==========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ==========================
    # RELATIONSHIP
    # ==========================
    user = db.relationship('User', backref='history_entries', foreign_keys=[user_id])

    # ==========================
    # STRING
    # ==========================
    def __repr__(self):
        return f"<History {self.username} {self.module} {self.action}>"