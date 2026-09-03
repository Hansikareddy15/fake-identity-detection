from flask import Flask, request, jsonify, render_template
from document_validator import validate_document
import json
import os

app = Flask(__name__)


# ==========================================
# DOCUMENT VALIDATION API
# ==========================================

@app.route("/validate", methods=["POST"])
def validate():

    document = request.get_json()

    if not document:
        return jsonify({
            "error": "No document data provided"
        }), 400

    result = validate_document(document)

    return jsonify(result), 200


# ==========================================
# VALIDATION HISTORY API
# ==========================================

@app.route("/history", methods=["GET"])
def history():

    log_file = "validation_logs.json"

    if not os.path.exists(log_file):

        return jsonify({
            "total_records": 0,
            "records": []
        }), 200

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            logs = json.load(file)

    except (json.JSONDecodeError, OSError):

        logs = []

    return jsonify({
        "total_records": len(logs),
        "records": logs
    }), 200


# ==========================================
# SEARCH HISTORY API
# ==========================================

@app.route("/search", methods=["GET"])
def search():

    search_text = request.args.get(
        "q",
        ""
    ).strip().lower()

    log_file = "validation_logs.json"

    if not os.path.exists(log_file):

        return jsonify({
            "total_records": 0,
            "records": []
        }), 200

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            logs = json.load(file)

    except (json.JSONDecodeError, OSError):

        logs = []


    if not search_text:

        results = logs

    else:

        results = []

        for record in logs:

            passport = str(
                record.get(
                    "passport_number",
                    ""
                )
            ).lower()

            name = str(
                record.get(
                    "name",
                    ""
                )
            ).lower()

            if (
                search_text in passport
                or search_text in name
            ):

                results.append(record)


    return jsonify({

        "total_records": len(results),

        "records": results

    }), 200


# ==========================================
# STATISTICS API
# ==========================================

@app.route("/statistics", methods=["GET"])
def statistics():

    log_file = "validation_logs.json"

    if not os.path.exists(log_file):

        return jsonify({
            "total_documents": 0,
            "valid": 0,
            "suspicious": 0,
            "invalid": 0,
            "tampering": {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0
            }
        }), 200

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            logs = json.load(file)

    except (json.JSONDecodeError, OSError):

        logs = []


    valid_count = 0
    suspicious_count = 0
    invalid_count = 0

    low_count = 0
    medium_count = 0
    high_count = 0


    for record in logs:

        status = record.get(
            "status",
            ""
        )

        tampering = record.get(
            "tampering_level",
            "LOW"
        )


        if status == "VALID":

            valid_count += 1

        elif status == "SUSPICIOUS":

            suspicious_count += 1

        elif status == "INVALID":

            invalid_count += 1


        if tampering == "LOW":

            low_count += 1

        elif tampering == "MEDIUM":

            medium_count += 1

        elif tampering == "HIGH":

            high_count += 1


    return jsonify({

        "total_documents": len(logs),

        "valid": valid_count,

        "suspicious": suspicious_count,

        "invalid": invalid_count,

        "tampering": {

            "LOW": low_count,

            "MEDIUM": medium_count,

            "HIGH": high_count
        }

    }), 200


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard", methods=["GET"])
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ==========================================
# HOME
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "message": "Document Validation System",

        "endpoints": [
            "/validate",
            "/history",
            "/search",
            "/statistics",
            "/dashboard"
        ]

    })


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )