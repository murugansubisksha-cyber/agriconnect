"""
AgriConnect Configuration File
Author: Team AgriConnect
Project: AI Smart Direct Farmer Marketplace
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure the sibling "database" folder exists (SQLite will fail to create
# the .db file if the parent folder doesn't exist yet).
_DB_DIR = os.path.join(BASE_DIR, "..", "database")
os.makedirs(_DB_DIR, exist_ok=True)


class Config:
    """
    Main Configuration Class
    """

    # =====================================================
    # FLASK SETTINGS
    # =====================================================

    SECRET_KEY = os.getenv("SECRET_KEY", "agriconnect_super_secret_key")

    DEBUG = True

    TESTING = False

    HOST = "127.0.0.1"

    PORT = 5000

    # =====================================================
    # DATABASE SETTINGS
    # =====================================================

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(BASE_DIR, "../database/agriconnect.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================================
    # JWT SETTINGS (required by auth.py / Flask-JWT-Extended)
    # =====================================================

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "agriconnect_super_secret_jwt_key")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=6)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_TOKEN_LOCATION = ["headers"]

    JWT_HEADER_NAME = "Authorization"

    JWT_HEADER_TYPE = "Bearer"

    # =====================================================
    # FILE UPLOAD SETTINGS
    # =====================================================

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # =====================================================
    # LANGUAGE SETTINGS
    # =====================================================

    DEFAULT_LANGUAGE = "English"

    SUPPORTED_LANGUAGES = [
        "English",
        "Tamil"
    ]

    # =====================================================
    # LOCATION SETTINGS
    # =====================================================

    COUNTRY = "India"

    TIMEZONE = "Asia/Kolkata"

    CURRENCY = "INR"

    DATE_FORMAT = "%d-%m-%Y"

    # =====================================================
    # WEATHER API
    # =====================================================

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

    # =====================================================
    # GOOGLE MAPS API
    # =====================================================

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    # =====================================================
    # TRANSLATION API
    # =====================================================

    TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")

    # =====================================================
    # PAYMENT SETTINGS
    # =====================================================

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")

    RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")

    # =====================================================
    # AI SETTINGS
    # =====================================================

    AI_ENABLED = True

    AI_MODEL = "Explainable AI Recommendation Engine"

    # =====================================================
    # VOICE ASSISTANT
    # =====================================================

    VOICE_ASSISTANT = True

    SPEECH_LANGUAGE = "ta-IN"

    # =====================================================
    # EMAIL SETTINGS
    # =====================================================

    MAIL_SERVER = os.getenv("MAIL_SERVER")

    MAIL_PORT = 587

    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # =====================================================
    # SECURITY SETTINGS
    # =====================================================

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SECURE = False

    REMEMBER_COOKIE_HTTPONLY = True

    # =====================================================
    # LOGGING
    # =====================================================

    LOG_LEVEL = "INFO"

    # =====================================================
    # CORS
    # =====================================================

    CORS_HEADERS = "Content-Type"

    # =====================================================
    # FUTURE MODULES
    # =====================================================

    ENABLE_CHATBOT = True

    ENABLE_NOTIFICATION = True

    ENABLE_ORDER_TRACKING = True

    ENABLE_QUOTATION_SYSTEM = True

    ENABLE_AI_RECOMMENDATION = True

    ENABLE_FARMER_VERIFICATION = True

    ENABLE_CUSTOMER_VERIFICATION = True


class DevelopmentConfig(Config):
    """Development environment: verbose errors, SQLite by default."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment: expects real secrets via environment variables."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


# Used by app.py to pick the right config class based on FLASK_ENV.
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}