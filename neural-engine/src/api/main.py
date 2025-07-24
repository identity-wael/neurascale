"""Main entry point for the Neural Engine API."""

from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def home():
    """Home endpoint."""
    return jsonify(
        {"service": "Neural Engine API", "version": "0.1.0", "status": "ready"}
    )


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    """Readiness check endpoint."""
    # TODO: Check actual service dependencies
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
