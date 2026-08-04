"""
quotation.py
============

Quotation management routes for AgriConnect (Flask).

Features:
    - Customer creates a quotation (offer) on a product
    - AI advisory score generated automatically (never auto-decides)
    - Farmer accepts/rejects the quotation
    - Customer can withdraw a still-pending quotation
    - View quotations by customer / by farmer
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from database import db
from models import AIRecommendation, Customer, Farmer, Product, Quotation

quotation_bp = Blueprint(
    "quotation",
    __name__,
    url_prefix="/api/quotations"
)


# ==========================================================
# Constants
# ==========================================================

VALID_QUOTATION_STATUS = (
    "Pending",
    "Accepted",
    "Rejected",
    "Expired",
    "Withdrawn",
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


def serialize_quotation(quotation):
    """Convert a Quotation model into JSON."""

    return {
        "quotation_id": quotation.quotation_id,
        "customer_id": quotation.customer_id,
        "product_id": quotation.product_id,
        "offered_price": quotation.offered_price,
        "requested_quantity": quotation.requested_quantity,
        "quotation_status": quotation.quotation_status,
        "quotation_deadline": (
            quotation.quotation_deadline.isoformat()
            if quotation.quotation_deadline else None
        ),
        "distance_from_farmer": quotation.distance_from_farmer,
        "ai_score": quotation.ai_score,
        "ai_recommended": quotation.ai_recommended,
        "farmer_decision": quotation.farmer_decision,
        "explanation_text": quotation.explanation_text,
        "created_at": (
            quotation.created_at.isoformat()
            if quotation.created_at else None
        ),
    }


def calculate_ai_advisory(product, customer, offered_price, requested_quantity, distance_km):
    """
    Simple, transparent 0-100 advisory score for a quotation.

    This is advisory ONLY -- it never changes quotation_status or
    farmer_decision. A farmer must always take the explicit action.

    Weighting: 35% price, 25% quantity fit, 20% distance, 20% buyer reliability.
    """

    # Price score: how close the offer is to the farmer's asking price
    if product.base_price and product.base_price > 0:
        price_ratio = offered_price / product.base_price
        price_score = max(0.0, min(100.0, price_ratio * 100))
    else:
        price_score = 50.0

    # Quantity score: how much of the available stock this order would use
    # (favors orders the farmer can actually fulfil)
    if product.available_quantity and product.available_quantity > 0:
        fit_ratio = requested_quantity / product.available_quantity
        if fit_ratio <= 1.0:
            quantity_score = 100.0 - (abs(0.5 - fit_ratio) * 60)
        else:
            quantity_score = 0.0
        quantity_score = max(0.0, min(100.0, quantity_score))
    else:
        quantity_score = 0.0

    # Distance score: closer buyers score higher (100km treated as far)
    if distance_km is None:
        distance_score = 50.0
    else:
        distance_score = max(0.0, min(100.0, 100.0 - (distance_km))) if distance_km <= 100 else 0.0

    # Reliability score: taken straight from the buyer's track record
    reliability_score = customer.reliability_score if customer.reliability_score is not None else 50.0

    overall = (
        (price_score * 0.35)
        + (quantity_score * 0.25)
        + (distance_score * 0.20)
        + (reliability_score * 0.20)
    )
    overall = round(max(0.0, min(100.0, overall)), 2)

    explanation = (
        f"Offer is {round((offered_price / product.base_price) * 100) if product.base_price else '--'}% "
        f"of asking price. Buyer reliability: {round(reliability_score)}/100. "
        f"Requested quantity fits {'within' if quantity_score > 0 else 'beyond'} available stock. "
        f"This score is advisory only -- you decide."
    )

    return {
        "price_score": round(price_score, 2),
        "quantity_score": round(quantity_score, 2),
        "distance_score": round(distance_score, 2),
        "reliability_score": round(reliability_score, 2),
        "overall_score": overall,
        "explanation": explanation,
    }


# ==========================================================
# Create Quotation (Customer)
# ==========================================================

@quotation_bp.route("/", methods=["POST"])
@jwt_required()
def create_quotation():
    """Customer sends an offer on a product."""

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can create quotations."
        }), 403

    data = request.get_json(silent=True) or {}

    required = ["product_id", "offered_price", "requested_quantity"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({
            "success": False,
            "message": f"Missing required fields: {', '.join(missing)}"
        }), 400

    product = Product.query.filter_by(
        product_id=data["product_id"], active_status=True
    ).first()

    if product is None:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    try:
        offered_price = float(data["offered_price"])
        requested_quantity = float(data["requested_quantity"])
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "offered_price and requested_quantity must be numbers."
        }), 400

    if offered_price <= 0 or requested_quantity <= 0:
        return jsonify({
            "success": False,
            "message": "offered_price and requested_quantity must be greater than 0."
        }), 400

    if requested_quantity > product.available_quantity:
        return jsonify({
            "success": False,
            "message": "Requested quantity exceeds available stock."
        }), 400

    distance_km = data.get("distance_from_farmer")

    quotation_deadline = None
    if data.get("quotation_deadline"):
        try:
            quotation_deadline = datetime.fromisoformat(data["quotation_deadline"])
        except ValueError:
            return jsonify({
                "success": False,
                "message": "quotation_deadline must be an ISO 8601 datetime."
            }), 400

    advisory = calculate_ai_advisory(
        product, user, offered_price, requested_quantity, distance_km
    )

    quotation = Quotation(
        customer_id=user.customer_id,
        product_id=product.product_id,
        offered_price=offered_price,
        requested_quantity=requested_quantity,
        quotation_status="Pending",
        quotation_deadline=quotation_deadline,
        distance_from_farmer=distance_km,
        ai_score=advisory["overall_score"],
        ai_recommended=advisory["overall_score"] >= 60,
        farmer_decision="Pending",
    )

    db.session.add(quotation)
    db.session.flush()  # get quotation.quotation_id before commit

    recommendation = AIRecommendation(
        quotation_id=quotation.quotation_id,
        recommendation_score=advisory["overall_score"],
        price_score=advisory["price_score"],
        quantity_score=advisory["quantity_score"],
        distance_score=advisory["distance_score"],
        reliability_score=advisory["reliability_score"],
        overall_score=advisory["overall_score"],
        explanation=advisory["explanation"],
    )
    db.session.add(recommendation)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Quotation submitted successfully.",
        "quotation": serialize_quotation(quotation),
        "ai_advisory": advisory
    }), 201


# ==========================================================
# Get Single Quotation
# ==========================================================

@quotation_bp.route("/<int:quotation_id>", methods=["GET"])
@jwt_required()
def get_quotation(quotation_id):

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    quotation = Quotation.query.filter_by(quotation_id=quotation_id).first()

    if quotation is None:
        return jsonify({"success": False, "message": "Quotation not found."}), 404

    if user_type == "customer" and quotation.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if user_type == "farmer" and quotation.product.farmer_id != user.farmer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    return jsonify({
        "success": True,
        "quotation": serialize_quotation(quotation)
    }), 200


# ==========================================================
# List Quotations -- Customer's Own
# ==========================================================

@quotation_bp.route("/customer", methods=["GET"])
@jwt_required()
def customer_quotations():

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    quotations = (
        Quotation.query
        .filter_by(customer_id=user.customer_id)
        .order_by(Quotation.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(quotations),
        "quotations": [serialize_quotation(q) for q in quotations]
    }), 200


# ==========================================================
# List Quotations -- Received by Farmer
# ==========================================================

@quotation_bp.route("/farmer", methods=["GET"])
@jwt_required()
def farmer_quotations():

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access this endpoint."
        }), 403

    quotations = (
        Quotation.query
        .join(Product, Quotation.product_id == Product.product_id)
        .filter(Product.farmer_id == user.farmer_id)
        .order_by(Quotation.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(quotations),
        "quotations": [serialize_quotation(q) for q in quotations]
    }), 200


# ==========================================================
# Farmer Decision (Accept / Reject)
# ==========================================================

@quotation_bp.route("/<int:quotation_id>/decision", methods=["PUT"])
@jwt_required()
def decide_quotation(quotation_id):
    """
    Farmer's explicit decision. This is the ONLY thing that can move a
    quotation out of 'Pending' -- the AI score never decides on its own.
    """

    user_type, user = current_user()

    if user_type != "farmer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can decide on quotations."
        }), 403

    quotation = Quotation.query.filter_by(quotation_id=quotation_id).first()

    if quotation is None:
        return jsonify({"success": False, "message": "Quotation not found."}), 404

    if quotation.product.farmer_id != user.farmer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if quotation.quotation_status != "Pending":
        return jsonify({
            "success": False,
            "message": f"Quotation already '{quotation.quotation_status}'."
        }), 400

    data = request.get_json(silent=True) or {}
    decision = data.get("decision")

    if decision not in ("Accepted", "Rejected"):
        return jsonify({
            "success": False,
            "message": "decision must be 'Accepted' or 'Rejected'."
        }), 400

    quotation.farmer_decision = decision
    quotation.quotation_status = decision
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Quotation {decision.lower()}.",
        "quotation": serialize_quotation(quotation)
    }), 200


# ==========================================================
# Withdraw Quotation (Customer)
# ==========================================================

@quotation_bp.route("/<int:quotation_id>/withdraw", methods=["PUT"])
@jwt_required()
def withdraw_quotation(quotation_id):

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can withdraw their own quotations."
        }), 403

    quotation = Quotation.query.filter_by(quotation_id=quotation_id).first()

    if quotation is None:
        return jsonify({"success": False, "message": "Quotation not found."}), 404

    if quotation.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    if quotation.quotation_status != "Pending":
        return jsonify({
            "success": False,
            "message": f"Cannot withdraw a quotation that is already '{quotation.quotation_status}'."
        }), 400

    quotation.quotation_status = "Withdrawn"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Quotation withdrawn.",
        "quotation": serialize_quotation(quotation)
    }), 200


# ==========================================================
# Blueprint Health Check
# ==========================================================

@quotation_bp.route("/status/ping", methods=["GET"])
def quotation_home():
    return jsonify({
        "success": True,
        "blueprint": "quotation",
        "status": "active"
    }), 200