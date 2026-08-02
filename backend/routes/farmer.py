"""
farmer.py
=========

Farmer management routes for AgriConnect.

Features
--------
- Public farmer profile
- Logged-in farmer profile
- Farmer dashboard
- Update farmer profile
- Farmer statistics
- Search farmers
- Verified farmers
- District/State filters
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from database import db
from models import Farmer, Product, Order


farmer_bp = Blueprint(
    "farmer",
    __name__,
    url_prefix="/api/farmers"
)


# ==========================================================
# Constants
# ==========================================================

VALID_FARMING_METHODS = (
    "Organic",
    "Conventional",
    "Natural",
)


# ==========================================================
# Helper Functions
# ==========================================================

def current_farmer():
    """
    Returns the currently logged-in farmer.
    Returns None if the logged-in user is not a farmer.
    """

    claims = get_jwt()

    if claims.get("user_type") != "farmer":
        return None

    farmer_id = int(get_jwt_identity())

    return Farmer.query.filter_by(
        farmer_id=farmer_id,
        active_status=True
    ).first()


def serialize_farmer(farmer):
    """
    Convert Farmer model into JSON.
    Password hash is intentionally excluded.
    """

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
        "registration_date": (
            farmer.registration_date.isoformat()
            if farmer.registration_date else None
        ),
        "active_status": farmer.active_status,
    }


def serialize_dashboard_product(product):
    """
    Small serializer used inside dashboard.
    """

    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "product_category": product.product_category,
        "available_quantity": product.available_quantity,
        "unit": product.unit,
        "base_price": product.base_price,
        "stock_status": product.stock_status,
        "organic_certified": product.organic_certified,
        "product_image": product.product_image,
    }


# ==========================================================
# Public Farmer Profile
# ==========================================================

@farmer_bp.route("/<int:farmer_id>", methods=["GET"])
def get_farmer(farmer_id):
    """
    Return a public farmer profile.
    """

    farmer = Farmer.query.filter_by(
        farmer_id=farmer_id,
        active_status=True
    ).first()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Farmer not found."
        }), 404

    return jsonify({
        "success": True,
        "farmer": serialize_farmer(farmer)
    }), 200


# ==========================================================
# Logged-in Farmer Profile
# ==========================================================

@farmer_bp.route("/me", methods=["GET"])
@jwt_required()
def my_profile():

    farmer = current_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access this endpoint."
        }), 403

    return jsonify({
        "success": True,
        "farmer": serialize_farmer(farmer)
    }), 200
# ==========================================================
# Get All Active Farmers
# ==========================================================

@farmer_bp.route("/", methods=["GET"])
def get_all_farmers():
    """
    Return all active farmers.
    """

    farmers = (
        Farmer.query
        .filter_by(active_status=True)
        .order_by(Farmer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200


# ==========================================================
# Get Verified Farmers
# ==========================================================

@farmer_bp.route("/verified", methods=["GET"])
def get_verified_farmers():
    """
    Return all verified farmers.
    """

    farmers = (
        Farmer.query
        .filter_by(
            active_status=True,
            verified_farmer=True
        )
        .order_by(Farmer.average_rating.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200


# ==========================================================
# Search Farmers
# ==========================================================

@farmer_bp.route("/search", methods=["GET"])
def search_farmers():
    """
    Search farmers by name.

    Example:
        /api/farmers/search?name=Ramesh
    """

    keyword = request.args.get("name", "").strip()

    if not keyword:
        return jsonify({
            "success": False,
            "message": "Search keyword is required."
        }), 400

    farmers = (
        Farmer.query
        .filter(
            Farmer.active_status == True,
            Farmer.full_name.ilike(f"%{keyword}%")
        )
        .order_by(Farmer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200


# ==========================================================
# Farmers By District
# ==========================================================

@farmer_bp.route("/district/<string:district>", methods=["GET"])
def farmers_by_district(district):
    """
    Return all farmers from a district.
    """

    farmers = (
        Farmer.query
        .filter(
            Farmer.active_status == True,
            Farmer.district.ilike(district)
        )
        .order_by(Farmer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "district": district,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200


# ==========================================================
# Farmers By State
# ==========================================================

@farmer_bp.route("/state/<string:state>", methods=["GET"])
def farmers_by_state(state):
    """
    Return all farmers from a state.
    """

    farmers = (
        Farmer.query
        .filter(
            Farmer.active_status == True,
            Farmer.state.ilike(state)
        )
        .order_by(Farmer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "state": state,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200
# ==========================================================
# Update Logged-in Farmer Profile
# ==========================================================

FARMER_UPDATABLE_FIELDS = {
    "full_name",
    "email",
    "farm_name",
    "farm_location",
    "district",
    "state",
    "pincode",
    "latitude",
    "longitude",
    "farming_method",
    "profile_photo",
    "farm_photo",
}


@farmer_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_farmer_profile():
    """
    Update the logged-in farmer profile.
    """

    farmer = current_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can update their profile."
        }), 403

    data = request.get_json(silent=True) or {}

    # ---------------- Email Validation ----------------

    if "email" in data and data["email"]:

        existing = Farmer.query.filter(
            Farmer.email == data["email"],
            Farmer.farmer_id != farmer.farmer_id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

    # ---------------- Farming Method Validation ----------------

    if "farming_method" in data:

        if data["farming_method"] not in VALID_FARMING_METHODS:
            return jsonify({
                "success": False,
                "message": "Invalid farming method."
            }), 400

    # ---------------- Update Allowed Fields ----------------

    for field, value in data.items():

        if field in FARMER_UPDATABLE_FIELDS:
            setattr(farmer, field, value)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully.",
        "farmer": serialize_farmer(farmer)
    }), 200


# ==========================================================
# Farmer Dashboard
# ==========================================================

@farmer_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def farmer_dashboard():
    """
    Dashboard for the logged-in farmer.
    """

    farmer = current_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access dashboard."
        }), 403

    recent_products = (
        Product.query
        .filter_by(
            farmer_id=farmer.farmer_id,
            active_status=True
        )
        .order_by(Product.created_at.desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "success": True,
        "dashboard": {
            "farmer": serialize_farmer(farmer),
            "statistics": {
                "total_products": farmer.total_products,
                "total_orders": farmer.total_orders,
                "average_rating": farmer.average_rating,
                "total_reviews": farmer.total_reviews
            },
            "recent_products": [
                serialize_dashboard_product(product)
                for product in recent_products
            ]
        }
    }), 200


# ==========================================================
# Farmer Statistics
# ==========================================================

@farmer_bp.route("/statistics", methods=["GET"])
@jwt_required()
def farmer_statistics():
    """
    Return statistics for the logged-in farmer.
    """

    farmer = current_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access statistics."
        }), 403

    total_products = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True
    ).count()

    in_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="In Stock"
    ).count()

    low_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="Low Stock"
    ).count()

    out_of_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="Out of Stock"
    ).count()
    total_orders = Order.query.filter_by(
        farmer_id=farmer.farmer_id
    ).count()

    completed_orders = Order.query.filter_by(
        farmer_id=farmer.farmer_id,
        order_status="Delivered"
    ).count()

    pending_orders = (
        Order.query.filter(
            Order.farmer_id == farmer.farmer_id,
            Order.order_status.in_([
                "Requested",
                "Accepted",
                "Packed",
                "Out for Delivery",
            ])
        ).count()
    )

    cancelled_orders = Order.query.filter_by(
        farmer_id=farmer.farmer_id,
        order_status="Cancelled"
    ).count()

    total_revenue = (
        db.session.query(db.func.sum(Order.total_amount))
        .filter(
            Order.farmer_id == farmer.farmer_id,
            Order.order_status == "Delivered"
        )
        .scalar()
    ) or 0.0

    return jsonify({
        "success": True,
        "statistics": {
            "total_products": total_products,
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "cancelled_orders": cancelled_orders,
            "average_rating": farmer.average_rating,
            "total_reviews": farmer.total_reviews,
            "estimated_revenue": total_revenue,
        }
    }), 200


# ==========================================================
# Top Rated Farmers
# ==========================================================

@farmer_bp.route("/top-rated", methods=["GET"])
def top_rated_farmers():
    """
    Return the top-rated active farmers.
    """

    farmers = (
        Farmer.query
        .filter_by(active_status=True)
        .order_by(
            Farmer.average_rating.desc(),
            Farmer.total_reviews.desc()
        )
        .limit(10)
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200


# ==========================================================
# Recently Registered Farmers
# ==========================================================

@farmer_bp.route("/recent", methods=["GET"])
def recent_farmers():
    """
    Return recently registered farmers.
    """

    farmers = (
        Farmer.query
        .filter_by(active_status=True)
        .order_by(Farmer.registration_date.desc())
        .limit(10)
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(farmers),
        "farmers": [
            serialize_farmer(farmer)
            for farmer in farmers
        ]
    }), 200