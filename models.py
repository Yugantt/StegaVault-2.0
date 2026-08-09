from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db



class User(db.Model):

    __tablename__ = "users"


    # ==========================
    # ID
    # ==========================

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # ==========================
    # USER INFO
    # ==========================

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )


    password = db.Column(
        db.String(255),
        nullable=False
    )


    # ==========================
    # PROFILE
    # ==========================

    full_name = db.Column(
        db.String(150),
        default=""
    )


    profile_image = db.Column(
        db.String(255),
        default="default.png"
    )


    # ==========================
    # ROLE
    # ==========================

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )


    # ==========================
    # STATUS
    # ==========================

    is_active = db.Column(
        db.Boolean,
        default=True
    )


    # ==========================
    # TIME
    # ==========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    last_login = db.Column(
        db.DateTime
    )


    # ==========================
    # PASSWORD
    # ==========================

    def set_password(self, password):

        self.password = generate_password_hash(password)



    def check_password(self, password):

        return check_password_hash(
            self.password,
            password
        )



    # ==========================
    # STRING
    # ==========================

    def __repr__(self):

        return f"<User {self.username}>"