"""
app.py - Flask web application for UPI Fraud Detection.
Provides a UI form for manual transaction input and a /predict API endpoint.
"""

import os
import sys
import json
from flask import Flask, request, render_template, jsonify
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.predict import predict_single, predict

app = Flask(__name__)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Render the main prediction form."""
    return render_template("index.html", features=config.FEATURE_COLUMNS)


@app.route("/predict", methods=["POST"])
def predict_form():
    """
    Handle form submission from the UI.
    Reads feature values, runs prediction, and renders result.
    """
    try:
        transaction = {}
        for feature in config.FEATURE_COLUMNS:
            raw = request.form.get(feature, 0)
            transaction[feature] = float(raw) if raw != "" else 0.0

        result = predict_single(transaction)
        return render_template(
            "index.html",
            features=config.FEATURE_COLUMNS,
            result=result,
            input_data=transaction,
        )
    except Exception as e:
        return render_template(
            "index.html",
            features=config.FEATURE_COLUMNS,
            error=str(e),
        )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    REST API endpoint for batch or single predictions.

    Accepts JSON body:
        - Single: {"amount": 0.5, "session_duration": -1.2, ...}
        - Batch:  [{"amount": 0.5, ...}, {"amount": 1.2, ...}]

    Returns:
        {
            "predictions":   [0, 1, ...],
            "probabilities": [0.12, 0.87, ...]
        }
    """
    data = request.get_json(force=True)
    if isinstance(data, dict):
        data = [data]

    df = pd.DataFrame(data)
    result = predict(df)
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model": config.MODEL_PATH})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host=config.APP_HOST, port=config.APP_PORT, debug=config.APP_DEBUG)
