"""
review.py
=========

Review and rating routes for AgriConnect (Flask).

Features:
    - Customer reviews a farmer, tied to one delivered order
      (verified-purchase-only, enforced by the unique order_id
      constraint on the Review model)
    - View / update / delete a review
    - Farmer's average_rating and total_reviews stay in sync
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from database import db
from models import Customer, Farmer, Order, Review

review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/api/reviews"
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


def serialize_review(review):
    return {
        "review_id": review.review_id,
        "customer_id": review.customer_id,
        "farmer_id": review.farmer_id,
        "order_id": review.order_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "review_date": (
            review.review_date.isoformat()
            if review.review_date else None
        ),
    }


def recalculate_farmer_rating(farmer):
    """Recompute a farmer's average_rating / total_reviews from their reviews."""

    reviews = farmer.reviews.all()
    farmer.total_reviews = len(reviews)
    farmer.average_rating = (
        round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else 0.0
    )


# ==========================================================
# Create Review (Customer, verified purchase only)
# ==========================================================

@review_bp.route("/", methods=["POST"])
@jwt_required()
def create_review():

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can leave reviews."
        }), 403

    data = request.get_json(silent=True) or {}

    order_id = data.get("order_id")
    rating = data.get("rating")

    if not order_id or rating is None:
        return jsonify({
            "success": False,
            "message": "order_id and rating are required."
        }), 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "rating must be an integer 1-5."}), 400

    if rating < 1 or rating > 5:
        return jsonify({"success": False, "message": "rating must be between 1 and 5."}), 400

    order = Order.query.filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({"success": False, "message": "Order not found."}), 404

    if order.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "This is not your order."}), 403

    if order.order_status != "Delivered":
        return jsonify({
            "success": False,
            "message": "You can only review an order after it has been delivered."
        }), 400

    if order.review is not None:
        return jsonify({
            "success": False,
            "message": "You have already reviewed this order."
        }), 409

    review = Review(
        customer_id=user.customer_id,
        farmer_id=order.farmer_id,
        order_id=order.order_id,
        rating=rating,
        review_text=data.get("review_text"),
    )

    db.session.add(review)
    db.session.flush()

    recalculate_farmer_rating(order.farmer)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Review submitted.",
        "review": serialize_review(review)
    }), 201


# ==========================================================
# Get Single Review
# ==========================================================

@review_bp.route("/<int:review_id>", methods=["GET"])
def get_review(review_id):

    review = Review.query.filter_by(review_id=review_id).first()

    if review is None:
        return jsonify({"success": False, "message": "Review not found."}), 404

    return jsonify({
        "success": True,
        "review": serialize_review(review)
    }), 200


# ==========================================================
# List Reviews For a Farmer (public)
# ==========================================================

@review_bp.route("/farmer/<int:farmer_id>", methods=["GET"])
def farmer_reviews(farmer_id):

    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()

    if farmer is None:
        return jsonify({"success": False, "message": "Farmer not found."}), 404

    reviews = (
        Review.query
        .filter_by(farmer_id=farmer_id)
        .order_by(Review.review_date.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "farmer_id": farmer_id,
        "average_rating": farmer.average_rating,
        "total_reviews": farmer.total_reviews,
        "count": len(reviews),
        "reviews": [serialize_review(r) for r in reviews]
    }), 200


# ==========================================================
# List Reviews -- Logged-in Customer's Own
# ==========================================================

@review_bp.route("/customer", methods=["GET"])
@jwt_required()
def customer_reviews():

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can access this endpoint."
        }), 403

    reviews = (
        Review.query
        .filter_by(customer_id=user.customer_id)
        .order_by(Review.review_date.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(reviews),
        "reviews": [serialize_review(r) for r in reviews]
    }), 200


# ==========================================================
# Update Review (Customer, own review only)
# ==========================================================

@review_bp.route("/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can edit their reviews."
        }), 403

    review = Review.query.filter_by(review_id=review_id).first()

    if review is None:
        return jsonify({"success": False, "message": "Review not found."}), 404

    if review.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    data = request.get_json(silent=True) or {}

    if "rating" in data:
        try:
            rating = int(data["rating"])
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "rating must be an integer 1-5."}), 400

        if rating < 1 or rating > 5:
            return jsonify({"success": False, "message": "rating must be between 1 and 5."}), 400

        review.rating = rating

    if "review_text" in data:
        review.review_text = data["review_text"]

    recalculate_farmer_rating(review.farmer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Review updated.",
        "review": serialize_review(review)
    }), 200


# ==========================================================
# Delete Review (Customer, own review only)
# ==========================================================

@review_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):

    user_type, user = current_user()

    if user_type != "customer" or user is None:
        return jsonify({
            "success": False,
            "message": "Only customers can delete their reviews."
        }), 403

    review = Review.query.filter_by(review_id=review_id).first()

    if review is None:
        return jsonify({"success": False, "message": "Review not found."}), 404

    if review.customer_id != user.customer_id:
        return jsonify({"success": False, "message": "Access denied."}), 403

    farmer = review.farmer
    db.session.delete(review)
    db.session.flush()

    recalculate_farmer_rating(farmer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Review deleted."
    }), 200


# ==========================================================
# Blueprint Health Check
# ==========================================================

@review_bp.route("/status/ping", methods=["GET"])
def review_home():
    return jsonify({
        "success": True,
        "blueprint": "review",
        "status": "active"
    }), 200