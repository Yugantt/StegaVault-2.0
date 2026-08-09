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
from werkzeug.utils import secure_filename
from config import Config
import os

# ======================================
# BLUEPRINT
# ======================================
profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/profile"
)

# ======================================
# PROFILE PAGE
# ======================================
@profile_bp.route("/")
def profile():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("auth.login"))

    # ==============================
    # GET USER STATS
    # ==============================
    from history import History
    
    stats = {
        "images_encoded": History.query.filter_by(
            user_id=user.id,
            module="Image",
            action="Encode"
        ).count(),
        
        "images_decoded": History.query.filter_by(
            user_id=user.id,
            module="Image",
            action="Decode"
        ).count(),
        
        "audio_files": History.query.filter_by(
            user_id=user.id,
            module="Audio"
        ).count(),
        
        "video_files": History.query.filter_by(
            user_id=user.id,
            module="Video"
        ).count()
    }

    return render_template(
        "dashboard/profile.html",
        user=user,
        stats=stats
    )

# ======================================
# UPDATE PROFILE
# ======================================
@profile_bp.route("/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    username = request.form.get("username")
    email = request.form.get("email")
    full_name = request.form.get("full_name")

    if username:
        # Check if username already exists (except current user)
        existing = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()
        if existing:
            flash("Username already taken.", "danger")
            return redirect(url_for("profile.profile"))
        user.username = username
        session["username"] = username  # Update session

    if email:
        # Check if email already exists (except current user)
        existing = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()
        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("profile.profile"))
        user.email = email

    if full_name:
        user.full_name = full_name

    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile.profile"))

# ======================================
# CHANGE PASSWORD
# ======================================
@profile_bp.route("/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        flash("All fields are required.", "danger")
        return redirect(url_for("profile.profile"))

    if not check_password_hash(user.password, current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("profile.profile"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile.profile"))

    if len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("profile.profile"))

    user.password = generate_password_hash(new_password)
    db.session.commit()

    flash("Password changed successfully!", "success")
    return redirect(url_for("profile.profile"))

# ======================================
# UPDATE PROFILE PICTURE
# ======================================
@profile_bp.route("/upload-picture", methods=["POST"])
def upload_picture():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    file = request.files.get("profile_image")

    if not file or file.filename == "":
        flash("Please select an image.", "danger")
        return redirect(url_for("profile.profile"))

    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        flash("Please upload a valid image (PNG, JPG, JPEG, GIF).", "danger")
        return redirect(url_for("profile.profile"))

    try:
        filename = secure_filename(f"user_{user.id}_{file.filename}")
        file_path = os.path.join(Config.PROFILE_FOLDER, filename)
        
        os.makedirs(Config.PROFILE_FOLDER, exist_ok=True)
        file.save(file_path)
        
        # Delete old profile picture if not default
        if user.profile_image and user.profile_image != "default.png":
            old_path = os.path.join(Config.PROFILE_FOLDER, user.profile_image)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
        
        user.profile_image = filename
        session["profile_image"] = filename  # Update session
        db.session.commit()
        
        flash("Profile picture updated successfully!", "success")
        
    except Exception as e:
        flash(f"Error uploading image: {str(e)}", "danger")
    
    return redirect(url_for("profile.profile"))