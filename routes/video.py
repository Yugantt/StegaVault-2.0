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
from extensions import db
from history import History
from utils import crypto, progress
from utils.video_steganography import CONTAINER, encode_video, decode_video

# ======================================
# BLUEPRINT
# ======================================
video_bp = Blueprint("video", __name__, url_prefix="/video")


def _is_ajax():
    return request.headers.get("X-Requested-With") == "fetch"


def _error(message, job_id=None):
    progress.fail(job_id, message)

    if _is_ajax():
        return jsonify({"success": False, "error": message}), 400

    flash(message, "danger")
    return redirect(url_for("video.video"))


def _log(action, filename, message, output_filename=None):
    record = History(
        username=session.get("username", "Unknown"),
        user_id=session.get("user_id"),
        module="Video",
        action=action,
        filename=filename,
        output_filename=output_filename,
        message=message[:50] + "..." if len(message) > 50 else message,
        status="Success"
    )
    db.session.add(record)
    db.session.commit()


# ======================================
# VIDEO PAGE
# ======================================
@video_bp.route("/")
def video():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard/video.html",
        decoded_message=""
    )


# ======================================
# ENCODE VIDEO
# ======================================
@video_bp.route("/encode", methods=["POST"])
def video_encode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading video...")

    file = request.files.get("video")
    message = request.form.get("message")
    password = (request.form.get("password") or "").strip()

    if not file or file.filename == "":
        return _error("Please select a video.", job_id)

    if not message or not message.strip():
        return _error("Please enter a secret message.", job_id)

    log_message = message

    if password:
        message = crypto.encrypt_message(message, password)
        log_message = "[Encrypted]"

    try:
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]

        upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        output_filename = f"{base_name}_stego{CONTAINER}"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

        file.save(upload_path)

        progress.set_progress(job_id, 2, "Encoding video...")

        encode_video(
            upload_path,
            output_path,
            message,
            progress_callback=progress.make_callback(job_id, "Encoding video...")
        )

        _log("Encode", filename, log_message, output_filename)

        progress.finish(job_id, "Encoding complete")

        if not _is_ajax():
            flash("Video encoded successfully!", "success")

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename
        )

    except ValueError as e:
        return _error(str(e), job_id)
    except Exception as e:
        return _error(f"Error: {str(e)}", job_id)


# ======================================
# DECODE VIDEO
# ======================================
@video_bp.route("/decode", methods=["POST"])
def video_decode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading video...")

    file = request.files.get("video")
    password = (request.form.get("password") or "").strip()

    if not file or file.filename == "":
        return _error("Please select a video.", job_id)

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, f"decode_{filename}")

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file.save(upload_path)

        progress.set_progress(job_id, 2, "Decoding video...")

        decoded_message = decode_video(
            upload_path,
            progress_callback=progress.make_callback(job_id, "Decoding video...")
        )

        if not decoded_message or not decoded_message.strip():
            decoded_message = "No hidden message found in this video."

        log_message = decoded_message

        if crypto.is_encrypted(decoded_message):
            if not password:
                return _error(
                    "This message is encrypted. Please enter the password.",
                    job_id
                )
            decoded_message = crypto.decrypt_message(decoded_message, password)
            log_message = "[Encrypted]"

        _log("Decode", filename, log_message)

        progress.finish(job_id, "Decoding complete")

        if _is_ajax():
            return jsonify({"success": True, "message": decoded_message})

        flash("Message decoded successfully!", "success")
        return render_template(
            "dashboard/video.html",
            decoded_message=decoded_message
        )

    except ValueError as e:
        return _error(str(e), job_id)
    except Exception as e:
        return _error(f"Error: {str(e)}", job_id)
