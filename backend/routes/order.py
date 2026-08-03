"""
order.py
========

Order management routes for AgriConnect.

Features
--------
- Create order from accepted quotation
- View order details
- Customer orders
- Farmer orders
- Update order status
- Update payment status
- Cancel order
- Delivered orders
- Pending orders
- Order statistics
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from database import db
from models import (
    Order,
    Quotation,
    Farmer,
    Customer,
    # If you have a Notification model, uncomment the next line:
    # Notification,
)

order_bp = Blueprint(
    "order",
    __name__,
    url_prefix="/api/orders"
)


# ==========================================================
# Constants
# ==========================================================

VALID_ORDER_STATUS = (
    "Requested",
    "Accepted",
    "Rejected",
    "Packed",
    "Out for Delivery",
    "Delivered",
    "Cancelled",
)

VALID_PAYMENT_STATUS = (
    "Pending",
    "Paid",
    "Failed",
    "Refunded",
)


# ==========================================================
# Helper Functions
# ==========================================================

def current_user():
    """
    Returns the logged-in user type and model object.
    """

    claims = get_jwt()

    user_type = claims.get("user_type")
    user_id = int(get_jwt_identity())

    if user_type == "farmer":
        return user_type, Farmer.query.filter_by(
            farmer_id=user_id,
            active_status=True
        ).first()

    if user_type == "customer":
        return user_type, Customer.query.filter_by(
            customer_id=user_id,
            active_status=True
        ).first()

    return None, None


def serialize_order(order):
    """
    Convert Order model into JSON.
    """

    return {
        "order_id": order.order_id,
        "quotation_id": order.quotation_id,
        "farmer_id": order.farmer_id,
        "customer_id": order.customer_id,
        "total_amount": order.total_amount,
        "delivery_charge": order.delivery_charge,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "order_date": (
            order.order_date.isoformat()
            if order.order_date else None
        ),
        "packed_date": (
            order.packed_date.isoformat()
            if order.packed_date else None
        ),
        "shipped_date": (
            order.shipped_date.isoformat()
            if order.shipped_date else None
        ),
        "delivered_date": (
            order.delivered_date.isoformat()
            if order.delivered_date else None
        ),
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
    }


def create_order_notification(user_id, message):
    """
    Helper to create a notification record.
    Requires a Notification model imported from models.py
    with fields: user_id, message, is_read.
    """
    from models import Notification  # local import to avoid hard dependency

    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False
    )

    db.session.add(notification)
    db.session.commit()


# ==========================================================
# Get Order By ID
# ==========================================================

@order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """
    Return a single order.

    Only the customer or farmer belonging to the
    order can access it.
    """

    user_type, user = current_user()

    if user is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized."
        }), 403

    order = Order.query.filter_by(
        order_id=order_id
    ).first()

    if order is None:
        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    if (
        user_type == "farmer"
        and order.farmer_id != user.farmer_id
    ):
        return jsonify({
            "success": False,
            "message": "Access denied."
        }), 403

    if (
        user_type == "customer"
        and order.customer_id != user.customer_id
    ):
        return jsonify({
            "success": False,
            "message": "Access denied."
        }), 403

    return jsonify({
        "success": True,
        "order": serialize_order(order)
    }), 200


# ==========================================================
# Customer Orders (supports optional ?status= filter)
# ==========================================================

@order_bp.route("/customer", methods=["GET"])
@jwt_required()
def customer_orders():
    """
    Return all orders of the logged-in customer.
    Optional query param: ?status=Delivered
    """

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    status = request.args.get("status")

    query = Order.query.filter_by(customer_id=user.customer_id)

    if status:
        query = query.filter_by(order_status=status)

    orders = query.order_by(Order.order_date.desc()).all()

    return jsonify({
        "success": True,
        "count": len(orders),
        "orders": [
            serialize_order(order)
            for order in orders
        ]
    }), 200


# ==========================================================
# Farmer Orders (supports optional ?status= filter)
# ==========================================================

@order_bp.route("/farmer", methods=["GET"])
@jwt_required()
def farmer_orders():
    """
    Return all orders of the logged-in farmer.
    Optional query param: ?status=Packed
    """

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access this endpoint."
        }), 403

    status = request.args.get("status")

    query = Order.query.filter_by(farmer_id=user.farmer_id)

    if status:
        query = query.filter_by(order_status=status)

    orders = query.order_by(Order.order_date.desc()).all()

    return jsonify({
        "success": True,
        "count": len(orders),
        "orders": [
            serialize_order(order)
            for order in orders
        ]
    }), 200


# ==========================================================
# Create Order From Accepted Quotation
# ==========================================================

@order_bp.route("/create", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create an order from an accepted quotation.
    """

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can create orders."
        }), 403

    data = request.get_json(silent=True) or {}

    quotation_id = data.get("quotation_id")

    if not quotation_id:
        return jsonify({
            "success": False,
            "message": "quotation_id is required."
        }), 400

    quotation = Quotation.query.filter_by(
        quotation_id=quotation_id
    ).first()

    if quotation is None:
        return jsonify({
            "success": False,
            "message": "Quotation not found."
        }), 404

    if quotation.product.farmer_id != user.farmer_id:
        return jsonify({
            "success": False,
            "message": "You do not own this quotation."
        }), 403

    if quotation.farmer_decision != "Accepted":
        return jsonify({
            "success": False,
            "message": "Quotation has not been accepted."
        }), 400

    existing_order = Order.query.filter_by(
        quotation_id=quotation.quotation_id
    ).first()

    if existing_order:
        return jsonify({
            "success": False,
            "message": "Order already exists for this quotation."
        }), 409

    total_amount = (
        quotation.offered_price *
        quotation.requested_quantity
    )

    order = Order(
        quotation_id=quotation.quotation_id,
        farmer_id=quotation.product.farmer_id,
        customer_id=quotation.customer_id,
        total_amount=total_amount,
        delivery_charge=data.get("delivery_charge", 0.0),
        payment_status="Pending",
        order_status="Requested"
    )

    db.session.add(order)

    user.total_orders += 1
    quotation.product.available_quantity -= quotation.requested_quantity

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order created successfully.",
        "order": serialize_order(order)
    }), 201


# ==========================================================
# Update Order Status (Farmer)
# ==========================================================

@order_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    """
    Farmer updates order status:
    Requested -> Accepted -> Packed -> Out for Delivery -> Delivered
    """

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can update order status."
        }), 403

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    if order.farmer_id != user.farmer_id:
        return jsonify({
            "success": False,
            "message": "You cannot modify this order."
        }), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in VALID_ORDER_STATUS:
        return jsonify({
            "success": False,
            "message": "Invalid order status."
        }), 400

    order.order_status = new_status

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order status updated successfully.",
        "order_id": order.order_id,
        "status": order.order_status
    }), 200


# ==========================================================
# Cancel Order (Customer)
# ==========================================================

@order_bp.route("/<int:order_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_order(order_id):
    """
    Customer cancels their own order, unless it has
    already shipped or been delivered.
    """

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can cancel orders."
        }), 403

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    if order.customer_id != user.customer_id:
        return jsonify({
            "success": False,
            "message": "This is not your order."
        }), 403

    if order.order_status in ("Out for Delivery", "Delivered"):
        return jsonify({
            "success": False,
            "message": "Cannot cancel a shipped or delivered order."
        }), 400

    order.order_status = "Cancelled"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order cancelled successfully."
    }), 200


# ==========================================================
# Order Statistics
# ==========================================================

@order_bp.route("/stats/summary", methods=["GET"])
@jwt_required()
def order_statistics():
    """
    Return order counts for the logged-in user.
    """

    user_type, user = current_user()

    if user_type == "farmer" and user is not None:
        orders = Order.query.filter_by(farmer_id=user.farmer_id).all()
    elif user_type == "customer" and user is not None:
        orders = Order.query.filter_by(customer_id=user.customer_id).all()
    else:
        return jsonify({
            "success": False,
            "message": "Invalid user role."
        }), 403

    total = len(orders)
    pending = len([o for o in orders if o.order_status == "Requested"])
    completed = len([o for o in orders if o.order_status == "Delivered"])

    return jsonify({
        "success": True,
        "total_orders": total,
        "pending_orders": pending,
        "completed_orders": completed
    }), 200


# ==========================================================
# Search Orders
# ==========================================================

@order_bp.route("/search", methods=["GET"])
@jwt_required()
def search_orders():
    """
    Search the logged-in user's orders by keyword,
    matching against order status or order id.
    """

    user_type, user = current_user()

    keyword = request.args.get("keyword", "")

    if user_type == "farmer" and user is not None:
        query = Order.query.filter_by(farmer_id=user.farmer_id)
    elif user_type == "customer" and user is not None:
        query = Order.query.filter_by(customer_id=user.customer_id)
    else:
        return jsonify({
            "success": False,
            "message": "Access denied."
        }), 403

    orders = query.all()

    matched_orders = [
        serialize_order(order)
        for order in orders
        if keyword.lower() in str(order.order_id).lower()
        or keyword.lower() in order.order_status.lower()
    ]

    return jsonify({
        "success": True,
        "results": matched_orders
    }), 200


# ==========================================================
# Update Payment Status
# ==========================================================

@order_bp.route("/<int:order_id>/payment", methods=["PUT"])
@jwt_required()
def update_payment_status(order_id):
    """
    Customer updates the payment status of their order.
    """

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can update payment status."
        }), 403

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    if order.customer_id != user.customer_id:
        return jsonify({
            "success": False,
            "message": "Only the order's customer can update payment."
        }), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in VALID_PAYMENT_STATUS:
        return jsonify({
            "success": False,
            "message": "Invalid payment status."
        }), 400

    order.payment_status = new_status

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Payment status updated.",
        "order_id": order.order_id,
        "payment_status": order.payment_status
    }), 200


# ==========================================================
# Final Router Check
# ==========================================================

@order_bp.route("/", methods=["GET"])
def order_home():
    return jsonify({
        "module": "Order Management",
        "status": "active",
        "features": [
            "Create Orders",
            "View Orders",
            "Update Status",
            "Cancel Orders",
            "Payment Tracking",
            "Order History",
        ]
    }), 200