"""
auth.py
=======
Authentication & account-management routes for AgriConnect.

Covers:
    - Farmer registration
    - Customer registration
    - Login (issues JWT access + refresh tokens)
    - Logout (revokes the current access token)
    - View profile
    - Update profile
    - Change password

Design notes
------------
Farmers and customers live in two separate tables (Farmer, Customer), so
a JWT alone (just a numeric "identity") isn't enough to know which table
to look in. We solve this by embedding a custom claim `user_type` into
every token: either "farmer" or "customer". Every protected route reads
that claim via `get_jwt()` to route the request to the right model.

JWT revocation ("logout") is stateless by default with JWT. We use a
simple in-memory blocklist of token IDs (`jti`) here for demo purposes.
In production, replace `BLOCKLIST` with a Redis set or a DB table so
revocation survives server restarts and works across multiple workers.
"""

import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models import Customer, Farmer

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ---------------------------------------------------------------------------
# In-memory JWT blocklist (demo only -- see docstring above)
# ---------------------------------------------------------------------------
BLOCKLIST: set[str] = set()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_REGEX = re.compile(r"^[6-9]\d{9}$")  # 10-digit Indian mobile number


def is_valid_email(email: str) -> bool:
    """Return True if `email` looks like a valid email address."""
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_valid_mobile(mobile: str) -> bool:
    """Return True if `mobile` is a valid 10-digit Indian mobile number."""
    return bool(mobile) and bool(MOBILE_REGEX.match(mobile))


def is_valid_password(password: str) -> bool:
    """Minimum password policy: at least 6 characters."""
    return bool(password) and len(password) >= 6


def missing_fields(data: dict, required: list[str]) -> list[str]:
    """Return the list of required fields that are missing/empty in `data`."""
    return [field for field in required if not str(data.get(field, "")).strip()]


# ---------------------------------------------------------------------------
# Serialization helpers (keep password_hash out of every response)
# ---------------------------------------------------------------------------
def serialize_farmer(farmer: Farmer) -> dict:
    return {
        "farmer_id": farmer.farmer_id,
        "full_name": farmer.full_name,
        "mobile_number": farmer.mobile_number,
        "email": farmer.email,
        "verified_farmer": farmer.verified_farmer,
        "farmer_badge": farmer.farmer_badge,
        "farm_name": farmer.farm_name,
        "farm_location": farmer.farm_location,
        "district": farmer.district,
        "state": farmer.state,
        "pincode": farmer.pincode,
        "latitude": farmer.latitude,
        "longitude": farmer.longitude,
        "farming_method": farmer.farming_method,
        "profile_photo": farmer.profile_photo,
        "farm_photo": farmer.farm_photo,
        "total_products": farmer.total_products,
        "total_orders": farmer.total_orders,
        "average_rating": farmer.average_rating,
        "total_reviews": farmer.total_reviews,
        "active_status": farmer.active_status,
        "registration_date": farmer.registration_date.isoformat() if farmer.registration_date else None,
    }


def serialize_customer(customer: Customer) -> dict:
    return {
        "customer_id": customer.customer_id,
        "full_name": customer.full_name,
        "mobile_number": customer.mobile_number,
        "email": customer.email,
        "profile_photo": customer.profile_photo,
        "address": customer.address,
        "district": customer.district,
        "state": customer.state,
        "pincode": customer.pincode,
        "latitude": customer.latitude,
        "longitude": customer.longitude,
        "reliability_score": customer.reliability_score,
        "successful_orders": customer.successful_orders,
        "cancelled_orders": customer.cancelled_orders,
        "total_orders": customer.total_orders,
        "average_rating": customer.average_rating,
        "active_status": customer.active_status,
    }


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
@auth_bp.route("/register/farmer", methods=["POST"])
def register_farmer():
    """Register a new farmer account."""
    data = request.get_json(silent=True) or {}

    required = ["full_name", "mobile_number", "password"]
    missing = missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    if not is_valid_mobile(data["mobile_number"]):
        return jsonify({"success": False, "message": "Invalid mobile number. Must be 10 digits."}), 400

    if not is_valid_password(data["password"]):
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    email = data.get("email", "").strip() or None
    if email and not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email address."}), 400

    # --- Duplicate checks ---
    if Farmer.query.filter_by(mobile_number=data["mobile_number"]).first():
        return jsonify({"success": False, "message": "Mobile number already registered."}), 409

    if email and Farmer.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered."}), 409

    aadhaar_number = data.get("aadhaar_number", "").strip() or None
    if aadhaar_number and Farmer.query.filter_by(aadhaar_number=aadhaar_number).first():
        return jsonify({"success": False, "message": "Aadhaar number already registered."}), 409

    farming_method = data.get("farming_method")
    if farming_method and farming_method not in ("Organic", "Conventional", "Natural"):
        return jsonify(
            {"success": False, "message": "farming_method must be Organic, Conventional, or Natural."}
        ), 400

    farmer = Farmer(
        full_name=data["full_name"].strip(),
        mobile_number=data["mobile_number"].strip(),
        email=email,
        password_hash=generate_password_hash(data["password"]),
        aadhaar_number=aadhaar_number,
        farm_name=data.get("farm_name"),
        farm_location=data.get("farm_location"),
        district=data.get("district"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        farming_method=farming_method,
    )

    db.session.add(farmer)
    db.session.commit()

    return jsonify({"success": True, "message": "Farmer registered successfully.", "farmer": serialize_farmer(farmer)}), 201


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer account."""
    data = request.get_json(silent=True) or {}

    required = ["full_name", "mobile_number", "password"]
    missing = missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    if not is_valid_mobile(data["mobile_number"]):
        return jsonify({"success": False, "message": "Invalid mobile number. Must be 10 digits."}), 400

    if not is_valid_password(data["password"]):
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    email = data.get("email", "").strip() or None
    if email and not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email address."}), 400

    # --- Duplicate checks ---
    if Customer.query.filter_by(mobile_number=data["mobile_number"]).first():
        return jsonify({"success": False, "message": "Mobile number already registered."}), 409

    if email and Customer.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered."}), 409

    customer = Customer(
        full_name=data["full_name"].strip(),
        mobile_number=data["mobile_number"].strip(),
        email=email,
        password_hash=generate_password_hash(data["password"]),
        address=data.get("address"),
        district=data.get("district"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify(
        {"success": True, "message": "Customer registered successfully.", "customer": serialize_customer(customer)}
    ), 201


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a farmer or customer.

    Expects JSON: { "user_type": "farmer" | "customer",
                     "mobile_number" or "email", "password" }
    """
    data = request.get_json(silent=True) or {}

    user_type = data.get("user_type")
    password = data.get("password")
    identifier = data.get("mobile_number") or data.get("email")

    if user_type not in ("farmer", "customer"):
        return jsonify({"success": False, "message": "user_type must be 'farmer' or 'customer'."}), 400

    if not identifier or not password:
        return jsonify({"success": False, "message": "mobile_number/email and password are required."}), 400

    model = Farmer if user_type == "farmer" else Customer
    user = model.query.filter(
        (model.mobile_number == identifier) | (model.email == identifier)
    ).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

    if not user.active_status:
        return jsonify({"success": False, "message": "This account has been deactivated."}), 403

    user_id = user.farmer_id if user_type == "farmer" else user.customer_id

    additional_claims = {"user_type": user_type}
    access_token = create_access_token(identity=str(user_id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user_id), additional_claims=additional_claims)

    serialized = serialize_farmer(user) if user_type == "farmer" else serialize_customer(user)

    return jsonify(
        {
            "success": True,
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_type": user_type,
            "user": serialized,
        }
    ), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Revoke the current access token by adding its jti to the blocklist."""
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
def _load_current_user():
    """
    Helper: resolve the logged-in Farmer or Customer object from the JWT.
    Returns (user_type, user_object) or (None, None) if not found.
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    user_type = claims.get("user_type")

    if user_type == "farmer":
        return user_type, Farmer.query.get(int(identity))
    if user_type == "customer":
        return user_type, Customer.query.get(int(identity))
    return None, None


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Return the logged-in user's profile."""
    user_type, user = _load_current_user()

    if user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    serialized = serialize_farmer(user) if user_type == "farmer" else serialize_customer(user)
    return jsonify({"success": True, "user_type": user_type, "user": serialized}), 200


# Fields each role is allowed to self-update. Anything not listed here
# (e.g. farmer_id, verified_farmer, average_rating, password_hash) is
# intentionally excluded to prevent users from tampering with protected data.
FARMER_UPDATABLE_FIELDS = {
    "full_name", "email", "farm_name", "farm_location", "district", "state",
    "pincode", "latitude", "longitude", "farming_method", "profile_photo", "farm_photo",
}
CUSTOMER_UPDATABLE_FIELDS = {
    "full_name", "email", "address", "district", "state", "pincode",
    "latitude", "longitude", "profile_photo",
}


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the logged-in user's editable profile fields."""
    user_type, user = _load_current_user()

    if user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    allowed_fields = FARMER_UPDATABLE_FIELDS if user_type == "farmer" else CUSTOMER_UPDATABLE_FIELDS

    new_email = data.get("email")
    if new_email:
        if not is_valid_email(new_email):
            return jsonify({"success": False, "message": "Invalid email address."}), 400
        model = Farmer if user_type == "farmer" else Customer
        existing = model.query.filter(model.email == new_email, model.__table__.c[
            "farmer_id" if user_type == "farmer" else "customer_id"
        ] != (user.farmer_id if user_type == "farmer" else user.customer_id)).first()
        if existing:
            return jsonify({"success": False, "message": "Email already in use."}), 409

    for field, value in data.items():
        if field in allowed_fields:
            setattr(user, field, value)

    db.session.commit()

    serialized = serialize_farmer(user) if user_type == "farmer" else serialize_customer(user)
    return jsonify({"success": True, "message": "Profile updated.", "user": serialized}), 200


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------
@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """Change the logged-in user's password."""
    user_type, user = _load_current_user()

    if user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "current_password and new_password are required."}), 400

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"success": False, "message": "Current password is incorrect."}), 401

    if not is_valid_password(new_password):
        return jsonify({"success": False, "message": "New password must be at least 6 characters."}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully."}), 200