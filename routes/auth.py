from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from extensions import db
from models import User
from login_log import record_login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)

# ======================================
# HOME / LOGIN PAGE
# ======================================

@auth_bp.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    
    return render_template("auth/login.html")

# ======================================
# REGISTER
# ======================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")
        
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("auth/register.html")
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template("auth/register.html")
        
        # Create user
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="admin" if User.query.count() == 0 else "user",
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

# ======================================
# LOGIN
# ======================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            flash("Please enter email and password.", "danger")
            return render_template("auth/login.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            record_login(request, "Failed", email, reason="Unknown email")
            flash("Invalid Email or Password!", "danger")
            return render_template("auth/login.html")
        
        if not check_password_hash(user.password, password):
            record_login(request, "Failed", email, user=user, reason="Wrong password")
            flash("Invalid Email or Password!", "danger")
            return render_template("auth/login.html")
        
        if not user.is_active:
            record_login(request, "Blocked", email, user=user, reason="Account locked")
            flash("Your account has been locked by an administrator.", "danger")
            return render_template("auth/login.html")
        
        record_login(request, "Success", email, user=user)
        
        # Login successful
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash(f"Welcome back, {user.username}!", "success")
        
        # Redirect based on role
        if user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return redirect(url_for("dashboard.dashboard"))
    
    return render_template("auth/login.html")

# ======================================
# LOGOUT
# ======================================

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))

# ======================================
# FORGOT PASSWORD (FIXED)
# ======================================

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email")
        
        if not email:
            flash("Please enter your email address.", "danger")
            return render_template("auth/forgot_password.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            
            # Store token in session for demo (in production, store in database)
            session['reset_token'] = token
            session['reset_email'] = email
            
            # Generate reset link
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            
            # Print to console for testing
            print("\n" + "="*70)
            print("🔑 PASSWORD RESET REQUEST")
            print("="*70)
            print(f"📧 Email: {email}")
            print(f"👤 Username: {user.username}")
            print(f"🔐 Token: {token}")
            print(f"🔗 Reset Link: {reset_link}")
            print("="*70 + "\n")
            
            flash("Password reset link has been sent to your email address! Check your console for the link.", "success")
            return redirect(url_for("auth.login"))
        else:
            # Security: Don't reveal if email exists
            flash("If an account exists with this email, you will receive reset instructions.", "info")
            return redirect(url_for("auth.login"))
    
    return render_template("auth/forgot_password.html")

# ======================================
# RESET PASSWORD (NEW)
# ======================================

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    
    # Verify token
    if not token or token != session.get('reset_token'):
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/reset_password.html", token=token)
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html", token=token)
        
        # Find user by email from session
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update password
            user.password = generate_password_hash(password)
            db.session.commit()
            
            # Clear reset session data
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            
            flash("Password reset successfully! Please login with your new password.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found. Please try again.", "danger")
            return redirect(url_for("auth.login"))
    
    return render_template("auth/reset_password.html", token=token)

# ======================================
# PROFILE
# ======================================

@auth_bp.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    user = User.query.get(session["user_id"])
    return render_template("auth/profile.html", user=user)

# ======================================
# UPDATE PROFILE
# ======================================

@auth_bp.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    user = User.query.get(session["user_id"])
    
    username = request.form.get("username")
    email = request.form.get("email")
    
    # Check if username already taken
    if username and username != user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.", "danger")
            return redirect(url_for("auth.profile"))
        user.username = username
    
    # Check if email already taken
    if email and email != user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.profile"))
        user.email = email
    
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for("auth.profile"))

# ======================================
# CHANGE PASSWORD
# ======================================

@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    user = User.query.get(session["user_id"])
    
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    
    if not old_password or not new_password or not confirm_password:
        flash("All fields are required.", "danger")
        return redirect(url_for("auth.profile"))
    
    if not check_password_hash(user.password, old_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("auth.profile"))
    
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("auth.profile"))
    
    if len(new_password) < 6:
        flash("Password must be at least 6 characters long.", "danger")
        return redirect(url_for("auth.profile"))
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    flash("Password changed successfully!", "success")
    return redirect(url_for("auth.profile"))