"""
=========================================================
AgriConnect
Database Configuration
=========================================================
Author : Team AgriConnect
Project: AI Smart Direct Farmer Marketplace
=========================================================
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Create SQLAlchemy object
db = SQLAlchemy()


class DatabaseManager:
    """
    Handles all database operations.
    """

    @staticmethod
    def initialize_database(app):
        """
        Connect Flask application with SQLAlchemy
        """

        db.init_app(app)

        with app.app_context():

            # Create all tables
            db.create_all()

            print("=====================================")
            print("AgriConnect Database Initialized")
            print("=====================================")

    @staticmethod
    def check_connection():
        """
        Test database connection.
        """

        try:
            db.session.execute(text("SELECT 1"))
            print("Database Connected Successfully")
            return True

        except Exception as error:
            print("Database Connection Failed")
            print(error)
            return False

    @staticmethod
    def commit():
        """
        Commit current transaction.
        """

        try:
            db.session.commit()

        except Exception as error:
            db.session.rollback()
            print(error)

    @staticmethod
    def rollback():
        """
        Rollback current transaction.
        """

        db.session.rollback()

    @staticmethod
    def close():
        """
        Close current database session.
        """

        db.session.remove()

    @staticmethod
    def create_tables():
        """
        Create all database tables.
        """

        db.create_all()

    @staticmethod
    def drop_tables():
        """
        Delete all database tables.
        """

        db.drop_all()

    @staticmethod
    def reset_database():
        """
        Reset the database completely.
        """

        db.drop_all()
        db.create_all()

        print("Database Reset Successfully")


def get_database():
    """
    Return SQLAlchemy object.
    """

    return db