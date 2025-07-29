"""Main entry point for the Neural Engine API."""

from flask import Flask, jsonify, Response
import logging
from flask_cors import CORS

from .device_api import device_api
from .visualization_api import visualization_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Register blueprints
app.register_blueprint(device_api)
app.register_blueprint(visualization_api)


@app.route("/")
def home() -> Response:
    """Home endpoint."""
    return jsonify(
        {"service": "Neural Engine API", "version": "0.1.0", "status": "ready"}
    )


@app.route("/health")
def health() -> tuple[Response, int]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready() -> tuple[Response, int]:
    """Readiness check endpoint."""
    # TODO: Check actual service dependencies
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
