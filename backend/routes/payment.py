"""
payment.py
==========

Payment management routes for AgriConnect (Flask).

Features:
    - Create a payment record for an order
    - View payment details
    - Update payment status (mock gateway callback)
    - Track a customer's / farmer's payment history
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from database import db
from models import Customer, Farmer, Order, Payment

payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/api/payments"
)


# ==========================================================
# Constants
# ==========================================================

VALID_PAYMENT_METHODS = (
    "UPI",
    "Debit Card",
    "Credit Card",
    "Net Banking",
    "Cash on Delivery",
)

VALID_PAYMENT_STATUS = (
    "Pending",
    "Success",
    "Failed",
    "Refunded",
)


# ==========================================================
# Helper Functions
# ==========================================================

def current_user():
    """Return (user_type, user_object) for the logged-in JWT identity."""

    claims = get_jwt()
    user_type = claims.get("user_type")
    user_id = int(get_jwt_identity())

    if user_type == "farmer":
        return user_type, Farmer.query.filter_by(
            farmer_id=user_id, active_status=True
        ).first()

    if user_type == "customer":
        return user_type, Customer.query.filter_by(
            customer_id=user_id, active_status=True
        ).first()

    return None, None


def serialize_payment(payment):
    return {
        "payment_id": payment.payment_id,
        "order_id": payment.order_id,
        "transaction_id": payment.transaction_id,
        "payment_method": payment.payment_method,
        "payment_status": payment.payment_status,
        "payment_amount": payment.payment_amount,
        "payment_date": (
            payment.payment_date.isoformat()
            if payment.payment_date else None
        ),
    }


# ==========================================================
# Create Payment (Customer)
# ==========================================================

@payment_bp.route("/", methods=["POST"])
@jwt_required()
def create_payment():
    """
    Customer initiates payment for their own order.
    On success, keeps Order.payment_status in sync.
    """

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can make payments."
        }), 403

    data = request.get_json(silent=True) or {}

    order_id = data.get("order_id")
    payment_method = data.get("payment_method")

    if not order_id or not payment_method:
        return jsonify({
            "success": False,
            "message": "order_id and payment_method are required."
        }), 400

    if payment_method not in VALID_PAYMENT_METHODS:
        return jsonify({
            "success": False,
            "message": f"payment_method must be one of {VALID_PAYMENT_METHODS}."
        }), 400

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({"success": False, "message": "Order not found."}), 404

    if order.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "This is not your order."}), 403

    if order.payment:
        return jsonify({
            "success": False,
            "message": "A payment record already exists for this order."
        }), 409

    # Mock gateway: Cash on Delivery starts Pending, everything else we
    # mark Success immediately since there's no real payment gateway wired up.
    status = "Pending" if payment_method == "Cash on Delivery" else "Success"

    payment = Payment(
        order_id=order.order_id,
        transaction_id=data.get("transaction_id"),
        payment_method=payment_method,
        payment_status=status,
        payment_amount=order.total_amount + (order.delivery_charge or 0.0),
    )

    db.session.add(payment)

    order.payment_status = "Paid" if status == "Success" else "Pending"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Payment recorded.",
        "payment": serialize_payment(payment)
    }), 201


# ==========================================================
# Get Single Payment
# ==========================================================

@payment_bp.route("/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    payment = Payment.query.filter_by(payment_id=payment_id).first()

    if payment is None:
        return jsonify({"success": False, "message": "Payment not found."}), 404

    order = payment.order

    if user_type == "customer" and order.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if user_type == "farmer" and order.farmer_id != user.farmer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    return jsonify({
        "success": True,
        "payment": serialize_payment(payment)
    }), 200


# ==========================================================
# Get Payment By Order
# ==========================================================

@payment_bp.route("/order/<int:order_id>", methods=["GET"])
@jwt_required()
def get_payment_by_order(order_id):

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({"success": False, "message": "Order not found."}), 404

    if user_type == "customer" and order.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if user_type == "farmer" and order.farmer_id != user.farmer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if order.payment is None:
        return jsonify({"success": False, "message": "No payment recorded for this order."}), 404

    return jsonify({
        "success": True,
        "payment": serialize_payment(order.payment)
    }), 200


# ==========================================================
# Update Payment Status
# ==========================================================

@payment_bp.route("/<int:payment_id>/status", methods=["PUT"])
@jwt_required()
def update_payment_status(payment_id):
    """
    Update a payment's status (e.g. Cash on Delivery collected -> Success,
    or a refund issued -> Refunded). Restricted to the customer who owns
    the order or the farmer fulfilling it.
    """

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    payment = Payment.query.filter_by(payment_id=payment_id).first()

    if payment is None:
        return jsonify({"success": False, "message": "Payment not found."}), 404

    order = payment.order

    if user_type == "customer" and order.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if user_type == "farmer" and order.farmer_id != user.farmer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("payment_status")

    if new_status not in VALID_PAYMENT_STATUS:
        return jsonify({
            "success": False,
            "message": f"payment_status must be one of {VALID_PAYMENT_STATUS}."
        }), 400

    payment.payment_status = new_status
    order.payment_status = "Paid" if new_status == "Success" else new_status

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Payment status updated.",
        "payment": serialize_payment(payment)
    }), 200


# ==========================================================
# List Payments -- Customer's Own
# ==========================================================

@payment_bp.route("/customer", methods=["GET"])
@jwt_required()
def customer_payments():

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    payments = (
        Payment.query
        .join(Order, Payment.order_id == Order.order_id)
        .filter(Order.customer_id == user.customer_id)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(payments),
        "payments": [serialize_payment(p) for p in payments]
    }), 200


# ==========================================================
# List Payments -- Farmer's Orders
# ==========================================================

@payment_bp.route("/farmer", methods=["GET"])
@jwt_required()
def farmer_payments():

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access this endpoint."
        }), 403

    payments = (
        Payment.query
        .join(Order, Payment.order_id == Order.order_id)
        .filter(Order.farmer_id == user.farmer_id)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(payments),
        "payments": [serialize_payment(p) for p in payments]
    }), 200


# ==========================================================
# Blueprint Health Check
# ==========================================================

@payment_bp.route("/status/ping", methods=["GET"])
def payment_home():
    return jsonify({
        "success": True,
        "blueprint": "payment",
        "status": "active"
    }), 200