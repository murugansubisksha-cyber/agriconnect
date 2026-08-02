"""
=========================================================
AgriConnect
Backend Package Initialization
=========================================================

Author  : Team AgriConnect
Project : AI Smart Direct Farmer Marketplace

=========================================================
"""

from flask import Flask
from flask_cors import CORS

# Import Configuration
from config import Config

# Import Database Manager
from database import DatabaseManager

# -------------------------------------------------------
# Create Flask Application
# -------------------------------------------------------

def create_app():
    """
    Creates and configures the Flask application.
    """

    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing
    CORS(app)

    # Initialize Database
    DatabaseManager.initialize_database(app)

    # ---------------------------------------------------
    # Register Routes
    # ---------------------------------------------------

    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp)
    except:
        pass

    try:
        from routes.farmer import farmer_bp
        app.register_blueprint(farmer_bp)
    except:
        pass

    try:
        from routes.customer import customer_bp
        app.register_blueprint(customer_bp)
    except:
        pass

    try:
        from routes.product import product_bp
        app.register_blueprint(product_bp)
    except:
        pass

    try:
        from routes.quotation import quotation_bp
        app.register_blueprint(quotation_bp)
    except:
        pass

    try:
        from routes.order import order_bp
        app.register_blueprint(order_bp)
    except:
        pass

    try:
        from routes.review import review_bp
        app.register_blueprint(review_bp)
    except:
        pass

    try:
        from routes.payment import payment_bp
        app.register_blueprint(payment_bp)
    except:
        pass

    try:
        from routes.chatbot import chatbot_bp
        app.register_blueprint(chatbot_bp)
    except:
        pass

    # ---------------------------------------------------
    # Home Route
    # ---------------------------------------------------

    @app.route("/")
    def home():
        return {
            "project": "AgriConnect",
            "description": "AI Smart Direct Farmer Marketplace",
            "status": "Backend Running Successfully"
        }

    return app