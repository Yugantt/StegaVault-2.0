from flask import Blueprint, jsonify, session

from utils import progress

progress_bp = Blueprint("progress", __name__, url_prefix="/progress")


@progress_bp.route("/<job_id>")
def job_progress(job_id):
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    job = progress.get(job_id)

    if job is None:
        return jsonify({
            "percent": 0,
            "stage": "Waiting...",
            "done": False,
            "error": None
        })

    return jsonify({
        "percent": job["percent"],
        "stage": job["stage"],
        "done": job["done"],
        "error": job["error"]
    })
