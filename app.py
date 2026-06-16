from flask import Flask, jsonify, request
import uuid
import threading
import os
import pandas as pd

from worker import process_job
from state_manager import (
    job_status,
    active_workers,
    cost_logs,
    cancel_flags
)

app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
OUTPUT_FOLDER = "data/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return jsonify({
        "message": "Solutory Procurement API Running",
        "status": "active"
    })


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    # Optional tracking ID for state collision testing
    tracking_id = request.form.get("tracking_id")

    if not tracking_id:
        tracking_id = str(uuid.uuid4())

    # ====================================
    # STATE COLLISION HANDLING
    # ====================================
    if (
        tracking_id in active_workers
        and active_workers[tracking_id].is_alive()
    ):

        cancel_flags[tracking_id] = True

        wasted_cost = job_status.get(
            tracking_id, {}
        ).get(
            "estimated_cost", 0
        )

        cost_logs[tracking_id] = {
            "wasted_cost": wasted_cost
        }

        audit_row = pd.DataFrame([
            {
                "tracking_id": tracking_id,
                "wasted_cost": wasted_cost
            }
        ])

        audit_file = os.path.join(
            OUTPUT_FOLDER,
            "cost_audit.csv"
        )

        if os.path.exists(audit_file):

            audit_row.to_csv(
                audit_file,
                mode="a",
                header=False,
                index=False
            )

        else:

            audit_row.to_csv(
                audit_file,
                index=False
            )

    # ====================================
    # SAVE FILE
    # ====================================
    file_path = os.path.join(
        UPLOAD_FOLDER,
        f"{tracking_id}_{file.filename}"
    )

    file.save(file_path)

    cancel_flags[tracking_id] = False

    # ====================================
    # INITIAL JOB STATE
    # ====================================
    job_status[tracking_id] = {
        "status": "processing",
        "progress": 0,
        "rows_processed": 0,
        "rows_quarantined": 0,
        "estimated_cost": 0,
        "file_path": file_path
    }

    # ====================================
    # START BACKGROUND WORKER
    # ====================================
    worker_thread = threading.Thread(
        target=process_job,
        args=(tracking_id, job_status)
    )

    worker_thread.daemon = True
    worker_thread.start()

    active_workers[tracking_id] = worker_thread

    return jsonify({
        "message": "File uploaded successfully",
        "tracking_id": tracking_id,
        "status": "processing"
    })


@app.route("/status/<tracking_id>", methods=["GET"])
def get_status(tracking_id):

    if tracking_id not in job_status:
        return jsonify({
            "error": "Tracking ID not found"
        }), 404

    return jsonify(job_status[tracking_id])


@app.route("/cancel/<tracking_id>", methods=["GET"])
def cancel_job(tracking_id):

    if tracking_id not in cancel_flags:
        return jsonify({
            "error": "Tracking ID not found"
        }), 404

    cancel_flags[tracking_id] = True

    wasted_cost = job_status.get(
        tracking_id, {}
    ).get(
        "estimated_cost", 0
    )

    cost_logs[tracking_id] = {
        "wasted_cost": wasted_cost
    }

    return jsonify({
        "message": "Job cancelled successfully",
        "wasted_cost": wasted_cost
    })


@app.route("/audit", methods=["GET"])
def audit():

    return jsonify(cost_logs)


if __name__ == "__main__":
    app.run(debug=True)