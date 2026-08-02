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
# Customer Orders
# ==========================================================

@order_bp.route("/customer", methods=["GET"])
@jwt_required()
def customer_orders():
    """
    Return all orders of the logged-in customer.
    """

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    orders = (
        Order.query
        .filter_by(customer_id=user.customer_id)
        .order_by(Order.order_date.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(orders),
        "orders": [
            serialize_order(order)
            for order in orders
        ]
    }), 200


# ==========================================================
# Farmer Orders
# ==========================================================

@order_bp.route("/farmer", methods=["GET"])
@jwt_required()
def farmer_orders():
    """
    Return all orders of the logged-in farmer.
    """

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access this endpoint."
        }), 403

    orders = (
        Order.query
        .filter_by(farmer_id=user.farmer_id)
        .order_by(Order.order_date.desc())
        .all()
    )

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
# ================================
# Update Order Status (Farmer)
# ================================

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Farmer updates order status:
    pending -> accepted -> packed -> shipped -> delivered
    """

    if current_user.role != "farmer":
        raise HTTPException(
            status_code=403,
            detail="Only farmers can update order status"
        )

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.farmer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot modify this order"
        )


    allowed_status = [
        "accepted",
        "packed",
        "shipped",
        "delivered",
        "cancelled"
    ]


    if status_update.status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )


    order.status = status_update.status

    db.commit()
    db.refresh(order)


    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }



# ================================
# Customer View Single Order
# ================================

@router.get("/{order_id}")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    if (
        order.customer_id != current_user.id
        and order.farmer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    return {
        "order_id": order.id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at
    }



# ================================
# Cancel Order (Customer)
# ================================

@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can cancel orders"
        )


    order = db.query(Order).filter(
        Order.id == order_id
    ).first()


    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="This is not your order"
        )


    if order.status in [
        "shipped",
        "delivered"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel shipped/delivered order"
        )


    order.status = "cancelled"

    db.commit()


    return {
        "message": "Order cancelled successfully"
    }
# ==========================================
# Farmer View Received Orders
# ==========================================

@router.get("/farmer/orders")
def get_farmer_orders(
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "farmer":
        raise HTTPException(
            status_code=403,
            detail="Only farmers can access orders"
        )


    query = db.query(Order).filter(
        Order.farmer_id == current_user.id
    )


    if status:
        query = query.filter(
            Order.status == status
        )


    orders = query.order_by(
        Order.created_at.desc()
    ).all()


    result = []

    for order in orders:
        result.append({
            "order_id": order.id,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at
        })


    return {
        "total_orders": len(result),
        "orders": result
    }



# ==========================================
# Customer Order History
# ==========================================

@router.get("/customer/history")
def get_customer_orders(
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can access order history"
        )


    query = db.query(Order).filter(
        Order.customer_id == current_user.id
    )


    if status:
        query = query.filter(
            Order.status == status
        )


    orders = query.order_by(
        Order.created_at.desc()
    ).all()


    order_list = []


    for order in orders:

        order_list.append({

            "order_id": order.id,

            "product_id": order.product_id,

            "quantity": order.quantity,

            "amount": order.total_price,

            "status": order.status,

            "date": order.created_at

        })


    return {

        "customer": current_user.id,

        "orders": order_list

    }



# ==========================================
# Order Statistics
# ==========================================

@router.get("/stats/summary")
def order_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role == "farmer":

        orders = db.query(Order).filter(
            Order.farmer_id == current_user.id
        ).all()


    elif current_user.role == "customer":

        orders = db.query(Order).filter(
            Order.customer_id == current_user.id
        ).all()


    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )


    total = len(orders)

    pending = len([
        o for o in orders
        if o.status == "pending"
    ])

    completed = len([
        o for o in orders
        if o.status == "delivered"
    ])


    return {

        "total_orders": total,

        "pending_orders": pending,

        "completed_orders": completed

    }
# ==========================================
# Search Orders
# ==========================================

@router.get("/search")
def search_orders(
    keyword: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    query = db.query(Order)


    if current_user.role == "farmer":

        query = query.filter(
            Order.farmer_id == current_user.id
        )


    elif current_user.role == "customer":

        query = query.filter(
            Order.customer_id == current_user.id
        )


    else:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    orders = query.all()


    matched_orders = []


    for order in orders:

        if (
            keyword.lower()
            in str(order.product_id).lower()
            or keyword.lower()
            in order.status.lower()
        ):

            matched_orders.append({

                "order_id": order.id,

                "product_id": order.product_id,

                "quantity": order.quantity,

                "price": order.total_price,

                "status": order.status

            })


    return {

        "results": matched_orders

    }



# ==========================================
# Update Payment Status
# ==========================================

@router.put("/{order_id}/payment")
def update_payment_status(
    order_id: int,
    payment_data: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()


    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    if order.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Only customer can update payment"
        )


    allowed_payment_status = [
        "pending",
        "paid",
        "failed"
    ]


    if payment_data.status not in allowed_payment_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )


    order.payment_status = payment_data.status


    db.commit()
    db.refresh(order)


    return {

        "message": "Payment status updated",

        "order_id": order.id,

        "payment_status": order.payment_status

    }



# ==========================================
# Notification Trigger Helper
# ==========================================

def create_order_notification(
    user_id,
    message,
    db
):

    notification = Notification(

        user_id=user_id,

        message=message,

        is_read=False

    )


    db.add(notification)

    db.commit()



# ==========================================
# Final Router Check
# ==========================================

@router.get("/")
def order_home():

    return {

        "module": "Order Management",

        "status": "active",

        "features": [

            "Create Orders",

            "View Orders",

            "Update Status",

            "Cancel Orders",

            "Payment Tracking",

            "Order History"

        ]

    }