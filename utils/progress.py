"""
Shared in-memory progress tracker for encode / decode jobs.

A job is identified by a client-generated job_id. The worker calls
set_progress() as it advances; the browser polls /progress/<job_id>.
"""

import threading
import time

_lock = threading.Lock()
_jobs = {}

# Jobs older than this (seconds) are discarded on the next access.
JOB_TTL = 600


def _purge_locked():
    now = time.time()
    stale = [
        job_id for job_id, job in _jobs.items()
        if now - job["updated_at"] > JOB_TTL
    ]
    for job_id in stale:
        del _jobs[job_id]


def start(job_id, stage="Starting..."):
    if not job_id:
        return

    with _lock:
        _purge_locked()
        _jobs[job_id] = {
            "percent": 0,
            "stage": stage,
            "done": False,
            "error": None,
            "updated_at": time.time(),
        }


def set_progress(job_id, percent, stage=None):
    if not job_id:
        return

    percent = max(0, min(100, int(percent)))

    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job["percent"] = percent
        if stage:
            job["stage"] = stage
        job["updated_at"] = time.time()


def finish(job_id, stage="Completed"):
    if not job_id:
        return

    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job["percent"] = 100
        job["stage"] = stage
        job["done"] = True
        job["updated_at"] = time.time()


def fail(job_id, error):
    if not job_id:
        return

    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job["error"] = str(error)
        job["stage"] = "Failed"
        job["done"] = True
        job["updated_at"] = time.time()


def get(job_id):
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return dict(job)


def make_callback(job_id, stage):
    """
    Returns a function(percent) that reports progress for this job,
    or None when there is no job_id (progress tracking disabled).
    """
    if not job_id:
        return None

    def callback(percent):
        set_progress(job_id, percent, stage)

    return callback
