"""
app.py
======
Application factory for AgriConnect.

Run locally with:
    py app.py          (Windows, as you normally invoke Python)

This creates the Flask app, wires up the database, JWT manager, and the
auth blueprint, and (for development only) auto-creates all tables from
models.py on first run.
"""

import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from auth import BLOCKLIST, auth_bp
from config import config_by_name
from database import db
from routes.product import product_bp
from routes.farmer import farmer_bp
from routes.customer import customer_bp
from routes.order import order_bp
from routes.quotation import quotation_bp
from routes.payment import payment_bp
from routes.review import review_bp
from routes.chatbot import chatbot_bp


def create_app(env: str = None) -> Flask:
    """Application factory: builds and returns a configured Flask app."""
    env = env or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    # --- Initialize extensions ---
    db.init_app(app)
    jwt = JWTManager(app)
    # Allow the future JS frontend (running on a different port) to call this API.
    CORS(app)

    # Import models so SQLAlchemy is aware of every table before create_all().
    import models  # noqa: F401

    # --- JWT blocklist check (powers the /auth/logout endpoint) ---
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has been revoked. Please log in again."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"success": False, "message": f"Invalid token: {reason}"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"success": False, "message": f"Authorization required: {reason}"}), 401

    # --- Register blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(quotation_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(chatbot_bp)

    # --- Simple health check route ---
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"success": True, "message": "AgriConnect API is running."}), 200

    # --- Dev convenience: auto-create tables if they don't exist ---
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)