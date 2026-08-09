import os
from datetime import timedelta
from dotenv import load_dotenv

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

# ==========================================
# Base Directory
# ==========================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INSTANCE_FOLDER = os.path.join(BASE_DIR, "instance")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")
PROFILE_FOLDER = os.path.join(BASE_DIR, "static", "profile")

# ==========================================
# Create Required Folders
# ==========================================

for folder in [
    INSTANCE_FOLDER,
    UPLOAD_FOLDER,
    OUTPUT_FOLDER,
    TEMP_FOLDER,
    PROFILE_FOLDER,
]:
    os.makedirs(folder, exist_ok=True)


class Config:

    # ======================================
    # Flask
    # ======================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "StegaVault-3.0-Super-Secret-Key"
    )

    DEBUG = True

    # ======================================
    # Database
    # ======================================

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(INSTANCE_FOLDER, "stegavault.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================================
    # Languages
    # ======================================

    BABEL_DEFAULT_LOCALE = "en"

    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, "translations")

    LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "es": "Spanish",
        "fr": "French"
    }

    # ======================================
    # Upload Directories
    # ======================================

    UPLOAD_FOLDER = UPLOAD_FOLDER
    OUTPUT_FOLDER = OUTPUT_FOLDER
    TEMP_FOLDER = TEMP_FOLDER
    PROFILE_FOLDER = PROFILE_FOLDER

    # ======================================
    # Upload Limit (500MB)
    # ======================================

    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    # ======================================
    # Allowed File Extensions (Combined)
    # ======================================

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "gif"
    }

    ALLOWED_AUDIO_EXTENSIONS = {
        "wav",
        "mp3",
        "flac",
        "aac"
    }

    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4",
        "avi",
        "mov",
        "mkv",
        "webm"
    }

    # ======================================
    # Combined Allowed Extensions
    # ======================================

    ALLOWED_EXTENSIONS = (
        ALLOWED_IMAGE_EXTENSIONS |
        ALLOWED_AUDIO_EXTENSIONS |
        ALLOWED_VIDEO_EXTENSIONS
    )

    # ======================================
    # Session
    # ======================================

    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # True in production with HTTPS

    # ======================================
    # Security
    # ======================================

    TEMPLATES_AUTO_RELOAD = True
    JSON_SORT_KEYS = False

    SEND_FILE_MAX_AGE_DEFAULT = 0

    # ======================================
    # CSRF Protection (Optional)
    # ======================================

    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", "csrf-secret-key")


# ==========================================
# Helper Functions
# ==========================================

def allowed_file(filename, allowed_extensions=None):
    """
    Check if a file has an allowed extension
    """
    if allowed_extensions is None:
        allowed_extensions = Config.ALLOWED_EXTENSIONS
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename):
    """
    Get file extension from filename
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None