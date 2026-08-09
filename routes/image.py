import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    flash,
    jsonify,
    session
)
from werkzeug.utils import secure_filename

from config import Config
from extensions import db
from history import History
from utils import crypto, progress
from utils.image_steganography import (
    encode_message_in_image,
    decode_message_from_image
)

# ======================================
# BLUEPRINT
# ======================================
image_bp = Blueprint("image", __name__, url_prefix="/image")


def _is_ajax():
    return request.headers.get("X-Requested-With") == "fetch"


def _error(message, job_id=None):
    progress.fail(job_id, message)

    if _is_ajax():
        return jsonify({"success": False, "error": message}), 400

    flash(message, "danger")
    return redirect(url_for("image.image"))


def _log(action, filename, message, output_filename=None):
    record = History(
        username=session.get("username", "Unknown"),
        user_id=session.get("user_id"),
        module="Image",
        action=action,
        filename=filename,
        output_filename=output_filename,
        message=message[:50] + "..." if len(message) > 50 else message,
        status="Success"
    )
    db.session.add(record)
    db.session.commit()


# ======================================
# IMAGE PAGE
# ======================================
@image_bp.route("/")
def image():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard/image.html",
        decoded_message=""
    )


# ======================================
# IMAGE ENCODE
# ======================================
@image_bp.route("/encode", methods=["POST"])
def image_encode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading image...")

    image_file = request.files.get("image")
    message = request.form.get("message")
    password = (request.form.get("password") or "").strip()

    if not image_file or image_file.filename == "":
        return _error("Please select an image.", job_id)

    if not message or not message.strip():
        return _error("Please enter a secret message.", job_id)

    log_message = message

    if password:
        message = crypto.encrypt_message(message, password)
        log_message = "[Encrypted]"

    try:
        filename = secure_filename(image_file.filename)
        base_name = os.path.splitext(filename)[0]

        upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        output_filename = f"{base_name}_stego.png"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

        image_file.save(upload_path)

        progress.set_progress(job_id, 5, "Encoding image...")

        encode_message_in_image(
            upload_path,
            message,
            output_path,
            progress_callback=progress.make_callback(job_id, "Encoding image...")
        )

        _log("Encode", filename, log_message, output_filename)

        progress.finish(job_id, "Encoding complete")

        if not _is_ajax():
            flash("Image encoded successfully!", "success")

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
# IMAGE DECODE
# ======================================
@image_bp.route("/decode", methods=["POST"])
def image_decode():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    job_id = request.form.get("job_id")
    progress.start(job_id, "Uploading image...")

    image_file = request.files.get("image")
    password = (request.form.get("password") or "").strip()

    if not image_file or image_file.filename == "":
        return _error("Please select an image.", job_id)

    try:
        filename = secure_filename(image_file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, f"decode_{filename}")

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        image_file.save(upload_path)

        progress.set_progress(job_id, 5, "Decoding image...")

        message = decode_message_from_image(
            upload_path,
            progress_callback=progress.make_callback(job_id, "Decoding image...")
        )

        if not message or not message.strip():
            message = "No hidden message found."

        log_message = message

        if crypto.is_encrypted(message):
            if not password:
                return _error(
                    "This message is encrypted. Please enter the password.",
                    job_id
                )
            message = crypto.decrypt_message(message, password)
            log_message = "[Encrypted]"

        _log("Decode", filename, log_message)

        progress.finish(job_id, "Decoding complete")

        if _is_ajax():
            return jsonify({"success": True, "message": message})

        flash("Message decoded successfully!", "success")
        return render_template(
            "dashboard/image.html",
            decoded_message=message
        )

    except ValueError as e:
        return _error(str(e), job_id)
    except Exception as e:
        return _error(f"Error: {str(e)}", job_id)
