"""
customer.py
===========

Customer management routes for AgriConnect.

Features
--------
- Public customer profile
- Logged-in customer profile
- Update customer profile
- Customer dashboard
- Customer statistics
- Search customers
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from database import db
from models import Customer, Order, Review


customer_bp = Blueprint(
    "customer",
    __name__,
    url_prefix="/api/customers"
)


# ==========================================================
# Helper Functions
# ==========================================================

def current_customer():
    """
    Return the currently logged-in customer.
    Returns None if the logged-in user is not a customer.
    """

    claims = get_jwt()

    if claims.get("user_type") != "customer":
        return None

    customer_id = int(get_jwt_identity())

    return Customer.query.filter_by(
        customer_id=customer_id,
        active_status=True
    ).first()


def serialize_customer(customer):
    """
    Convert Customer model into JSON.
    Password hash is intentionally excluded.
    """

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
        "created_at": (
            customer.created_at.isoformat()
            if customer.created_at else None
        ),
    }


# ==========================================================
# Public Customer Profile
# ==========================================================

@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """
    Return a public customer profile.
    """

    customer = Customer.query.filter_by(
        customer_id=customer_id,
        active_status=True
    ).first()

    if customer is None:
        return jsonify({
            "success": False,
            "message": "Customer not found."
        }), 404

    return jsonify({
        "success": True,
        "customer": serialize_customer(customer)
    }), 200


# ==========================================================
# Logged-in Customer Profile
# ==========================================================

@customer_bp.route("/me", methods=["GET"])
@jwt_required()
def my_profile():
    """
    Return the logged-in customer's profile.
    """

    customer = current_customer()

    if customer is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    return jsonify({
        "success": True,
        "customer": serialize_customer(customer)
    }), 200
# ==========================================================
# Get All Active Customers
# ==========================================================

@customer_bp.route("/", methods=["GET"])
def get_all_customers():
    """
    Return all active customers.
    """

    customers = (
        Customer.query
        .filter_by(active_status=True)
        .order_by(Customer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(customers),
        "customers": [
            serialize_customer(customer)
            for customer in customers
        ]
    }), 200


# ==========================================================
# Search Customers
# ==========================================================

@customer_bp.route("/search", methods=["GET"])
def search_customers():
    """
    Search customers by name.

    Example:
        /api/customers/search?name=Arun
    """

    keyword = request.args.get("name", "").strip()

    if not keyword:
        return jsonify({
            "success": False,
            "message": "Search keyword is required."
        }), 400

    customers = (
        Customer.query
        .filter(
            Customer.active_status == True,
            Customer.full_name.ilike(f"%{keyword}%")
        )
        .order_by(Customer.full_name.asc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(customers),
        "customers": [
            serialize_customer(customer)
            for customer in customers
        ]
    }), 200


# ==========================================================
# Update Logged-in Customer Profile
# ==========================================================

CUSTOMER_UPDATABLE_FIELDS = {
    "full_name",
    "email",
    "address",
    "district",
    "state",
    "pincode",
    "latitude",
    "longitude",
    "profile_photo",
}


@customer_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_customer_profile():
    """
    Update the logged-in customer's profile.
    """

    customer = current_customer()

    if customer is None:
        return jsonify({
            "success": False,
            "message": "Only customers can update their profile."
        }), 403

    data = request.get_json(silent=True) or {}

    # ---------------- Email Validation ----------------

    if "email" in data and data["email"]:

        existing = Customer.query.filter(
            Customer.email == data["email"],
            Customer.customer_id != customer.customer_id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

    # ---------------- Update Fields ----------------

    for field, value in data.items():

        if field in CUSTOMER_UPDATABLE_FIELDS:
            setattr(customer, field, value)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully.",
        "customer": serialize_customer(customer)
    }), 200
# ==========================================================
# Customer Dashboard
# ==========================================================

@customer_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def customer_dashboard():
    """
    Dashboard for the logged-in customer.
    """

    customer = current_customer()

    if customer is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access dashboard."
        }), 403

    recent_orders = (
        Order.query
        .filter_by(customer_id=customer.customer_id)
        .order_by(Order.order_date.desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "success": True,
        "dashboard": {
            "customer": serialize_customer(customer),
            "statistics": {
                "total_orders": customer.total_orders,
                "successful_orders": customer.successful_orders,
                "cancelled_orders": customer.cancelled_orders,
                "average_rating": customer.average_rating,
                "reliability_score": customer.reliability_score,
            },
            "recent_orders": [
                {
                    "order_id": order.order_id,
                    "quotation_id": order.quotation_id,
                    "total_amount": order.total_amount,
                    "payment_status": order.payment_status,
                    "order_status": order.order_status,
                    "order_date": (
                        order.order_date.isoformat()
                        if order.order_date else None
                    ),
                }
                for order in recent_orders
            ]
        }
    }), 200


# ==========================================================
# Customer Statistics
# ==========================================================

@customer_bp.route("/statistics", methods=["GET"])
@jwt_required()
def customer_statistics():
    """
    Return statistics for the logged-in customer.
    """

    customer = current_customer()

    if customer is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access statistics."
        }), 403

    total_orders = Order.query.filter_by(
        customer_id=customer.customer_id
    ).count()

    delivered_orders = Order.query.filter_by(
        customer_id=customer.customer_id,
        order_status="Delivered"
    ).count()

    pending_orders = (
        Order.query.filter(
            Order.customer_id == customer.customer_id,
            Order.order_status.in_([
                "Requested",
                "Accepted",
                "Packed",
                "Out for Delivery"
            ])
        ).count()
    )

    cancelled_orders = Order.query.filter_by(
        customer_id=customer.customer_id,
        order_status="Cancelled"
    ).count()
    total_spent = (
        db.session.query(db.func.sum(Order.total_amount))
        .filter(
            Order.customer_id == customer.customer_id,
            Order.order_status == "Delivered"
        )
        .scalar()
    ) or 0.0

    total_reviews = Review.query.filter_by(
        customer_id=customer.customer_id
    ).count()

    return jsonify({
        "success": True,
        "statistics": {
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "pending_orders": pending_orders,
            "cancelled_orders": cancelled_orders,
            "total_reviews": total_reviews,
            "average_rating": customer.average_rating,
            "reliability_score": customer.reliability_score,
            "total_spent": total_spent
        }
    }), 200