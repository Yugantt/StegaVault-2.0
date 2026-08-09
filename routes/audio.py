import os

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
    send_file
)
from werkzeug.utils import secure_filename

from config import Config
from utils import crypto, progress
from utils.audio_steganography import encode_audio_lsb, decode_audio_lsb

# ======================================
# BLUEPRINT
# ======================================
audio_bp = Blueprint("audio", __name__, url_prefix="/audio")


def _is_ajax():
    return request.headers.get("X-Requested-With") == "fetch"


def _error(message, job_id=None):
    """
    Report a failure either as JSON (AJAX) or as a flash + redirect.
    """
    progress.fail(job_id, message)

    if _is_ajax():
        return jsonify({"success": False, "error": message}), 400

    flash(message, "danger")
    return redirect(url_for("audio.audio"))


# ======================================
# AUDIO PAGE
# ======================================
@audio_bp.route("/")
def audio():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard/audio.html",
        decoded_message=""
    )


# ======================================
# ENCODE AUDIO
# ======================================
@audio_bp.route("/encode", methods=["POST"])
def audio_encode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading audio...")

    audio_file = request.files.get("audio")
    message = request.form.get("message")
    password = (request.form.get("password") or "").strip()

    if not audio_file or audio_file.filename == "":
        return _error("Please select an audio file.", job_id)

    if not message or not message.strip():
        return _error("Please enter a secret message.", job_id)

    if not audio_file.filename.lower().endswith(".wav"):
        return _error("Please upload a WAV audio file.", job_id)

    if password:
        message = crypto.encrypt_message(message, password)

    try:
        filename = secure_filename(audio_file.filename)
        base_name = os.path.splitext(filename)[0]

        upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        output_filename = f"{base_name}_stego.wav"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

        audio_file.save(upload_path)

        progress.set_progress(job_id, 5, "Encoding audio...")

        encode_audio_lsb(
            upload_path,
            message,
            output_path,
            progress_callback=progress.make_callback(job_id, "Encoding audio...")
        )

        progress.finish(job_id, "Encoding complete")

        if not _is_ajax():
            flash("Audio encoded successfully!", "success")

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename
        )

    except ValueError as e:
        return _error(str(e), job_id)
    except Exception as e:
        return _error(f"An error occurred: {str(e)}", job_id)


# ======================================
# DECODE AUDIO
# ======================================
@audio_bp.route("/decode", methods=["POST"])
def audio_decode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading audio...")

    audio_file = request.files.get("audio")
    password = (request.form.get("password") or "").strip()

    if not audio_file or audio_file.filename == "":
        return _error("Please select an audio file.", job_id)

    if not audio_file.filename.lower().endswith(".wav"):
        return _error("Please upload a WAV audio file.", job_id)

    try:
        filename = secure_filename(audio_file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, f"decode_{filename}")

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        audio_file.save(upload_path)

        progress.set_progress(job_id, 5, "Decoding audio...")

        message = decode_audio_lsb(
            upload_path,
            progress_callback=progress.make_callback(job_id, "Decoding audio...")
        )

        if not message or not message.strip():
            message = "No hidden message found in this audio."

        if crypto.is_encrypted(message):
            if not password:
                return _error(
                    "This message is encrypted. Please enter the password.",
                    job_id
                )
            message = crypto.decrypt_message(message, password)

        progress.finish(job_id, "Decoding complete")

        if _is_ajax():
            return jsonify({"success": True, "message": message})

        flash("Message decoded successfully!", "success")
        return render_template(
            "dashboard/audio.html",
            decoded_message=message
        )

    except ValueError as e:
        return _error(str(e), job_id)
    except Exception as e:
        return _error(f"Error decoding: {str(e)}", job_id)
