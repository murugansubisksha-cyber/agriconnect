"""
models.py
=========
AgriConnect - AI-Powered Direct Farmer Marketplace
Flask-SQLAlchemy Data Models

This module defines all database models for the AgriConnect platform.
Designed for SQLite in development, with full compatibility for
migration to PostgreSQL / MySQL in production (no SQLite-only types used).

Conventions followed across all models:
    - Primary key: `<model>_id` (Integer, autoincrement)
    - `created_at` / `updated_at` timestamps (UTC, auto-managed)
    - `active_status` boolean flag for soft-deletion / deactivation
    - Explicit foreign keys and relationship() declarations
    - CheckConstraint / UniqueConstraint for data integrity
    - __repr__() for debugging/logging readability

Import `db` from this module's `database.py` companion file. This file
assumes a `db = SQLAlchemy()` instance is created in `database.py` and
initialized on the Flask app via `db.init_app(app)` in `config.py` / `app.py`.
"""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import foreign, validates

from database import db


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def utcnow():
    """Return current UTC datetime (timezone-aware) for default timestamps."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# 1. Farmer Model
# ---------------------------------------------------------------------------
class Farmer(db.Model):
    """
    Represents a farmer/seller registered on AgriConnect.

    A farmer can list multiple products, receive reviews from customers,
    exchange chat messages, and receive notifications.
    """

    __tablename__ = "farmers"

    farmer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # --- Personal / Auth details ---
    full_name = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=True, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    aadhaar_number = db.Column(db.String(20), nullable=True, unique=True)

    # --- Verification / Trust ---
    verified_farmer = db.Column(db.Boolean, default=False, nullable=False)
    farmer_badge = db.Column(db.String(50), nullable=True)  # e.g. "Gold", "Trusted Seller"

    # --- Farm details ---
    farm_name = db.Column(db.String(150), nullable=True)
    farm_location = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(100), nullable=True, index=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    farming_method = db.Column(db.String(20), nullable=True)  # Organic / Conventional / Natural

    # --- Media ---
    profile_photo = db.Column(db.String(255), nullable=True)  # file path / URL
    farm_photo = db.Column(db.String(255), nullable=True)

    # --- Aggregated stats (denormalized for fast dashboard reads) ---
    total_products = db.Column(db.Integer, default=0, nullable=False)
    total_orders = db.Column(db.Integer, default=0, nullable=False)
    average_rating = db.Column(db.Float, default=0.0, nullable=False)
    total_reviews = db.Column(db.Integer, default=0, nullable=False)

    # --- Status / Timestamps ---
    registration_date = db.Column(db.DateTime, default=utcnow, nullable=False)
    active_status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # --- Relationships ---
    products = db.relationship(
        "Product", back_populates="farmer", cascade="all, delete-orphan", lazy="dynamic"
    )
    orders = db.relationship("Order", back_populates="farmer", lazy="dynamic")
    reviews = db.relationship("Review", back_populates="farmer", lazy="dynamic")
    sent_chats = db.relationship(
        "Chat",
        primaryjoin="and_(foreign(Chat.sender_id)==Farmer.farmer_id, Chat.sender_type=='farmer')",
        back_populates="sender_farmer",
        viewonly=True,
        lazy="dynamic",
    )
    notifications = db.relationship(
        "Notification",
        primaryjoin="and_(Notification.user_id==Farmer.farmer_id, "
        "Notification.user_type=='farmer')",
        foreign_keys="Notification.user_id",
        lazy="dynamic",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint(
            "farming_method IN ('Organic', 'Conventional', 'Natural')",
            name="ck_farmer_farming_method",
        ),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="ck_farmer_avg_rating"),
    )

    def __repr__(self):
        return f"<Farmer id={self.farmer_id} name='{self.full_name}' verified={self.verified_farmer}>"


# ---------------------------------------------------------------------------
# 2. Customer Model
# ---------------------------------------------------------------------------
class Customer(db.Model):
    """
    Represents a buyer/customer registered on AgriConnect.

    A customer can send quotations, place orders, write reviews, and chat
    with farmers. `reliability_score` reflects buying trustworthiness and
    is kept in sync with the BuyerReliability model.
    """

    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    full_name = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=True, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255), nullable=True)

    address = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(100), nullable=True, index=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # --- Reliability / order stats (denormalized snapshot; source of truth
    #     for the detailed breakdown lives in BuyerReliability) ---
    reliability_score = db.Column(db.Float, default=50.0, nullable=False)
    successful_orders = db.Column(db.Integer, default=0, nullable=False)
    cancelled_orders = db.Column(db.Integer, default=0, nullable=False)
    total_orders = db.Column(db.Integer, default=0, nullable=False)
    average_rating = db.Column(db.Float, default=0.0, nullable=False)

    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    active_status = db.Column(db.Boolean, default=True, nullable=False)

    # --- Relationships ---
    quotations = db.relationship("Quotation", back_populates="customer", lazy="dynamic")
    orders = db.relationship("Order", back_populates="customer", lazy="dynamic")
    reviews = db.relationship("Review", back_populates="customer", lazy="dynamic")
    sent_chats = db.relationship(
        "Chat",
        primaryjoin="and_(foreign(Chat.sender_id)==Customer.customer_id, Chat.sender_type=='customer')",
        back_populates="sender_customer",
        viewonly=True,
        lazy="dynamic",
    )
    reliability_detail = db.relationship(
        "BuyerReliability", back_populates="customer", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 100", name="ck_customer_reliability"
        ),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="ck_customer_avg_rating"),
    )

    def __repr__(self):
        return f"<Customer id={self.customer_id} name='{self.full_name}'>"


# ---------------------------------------------------------------------------
# 3. Product Model
# ---------------------------------------------------------------------------
class Product(db.Model):
    """
    Represents a crop/produce listing created by a farmer.

    Each product belongs to exactly one farmer and can receive many
    quotations from interested customers.
    """

    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(
        db.Integer, db.ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True
    )

    product_name = db.Column(db.String(150), nullable=False)
    product_category = db.Column(db.String(80), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)

    harvest_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)

    available_quantity = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(20), nullable=False, default="kg")  # kg, quintal, ton, dozen...

    base_price = db.Column(db.Float, nullable=False)      # price per unit, farmer's asking price
    minimum_price = db.Column(db.Float, nullable=True)    # lowest price farmer will accept

    product_image = db.Column(db.String(255), nullable=True)

    delivery_available = db.Column(db.Boolean, default=False, nullable=False)
    pickup_available = db.Column(db.Boolean, default=True, nullable=False)

    stock_status = db.Column(db.String(20), default="In Stock", nullable=False)
    # Values: In Stock / Low Stock / Out of Stock

    organic_certified = db.Column(db.Boolean, default=False, nullable=False)

    active_status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # --- Relationships ---
    farmer = db.relationship("Farmer", back_populates="products")
    quotations = db.relationship(
        "Quotation", back_populates="product", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (
        CheckConstraint("base_price > 0", name="ck_product_base_price_positive"),
        CheckConstraint("available_quantity >= 0", name="ck_product_quantity_non_negative"),
        CheckConstraint(
            "stock_status IN ('In Stock', 'Low Stock', 'Out of Stock')",
            name="ck_product_stock_status",
        ),
    )

    def __repr__(self):
        return f"<Product id={self.product_id} name='{self.product_name}' farmer_id={self.farmer_id}>"


# ---------------------------------------------------------------------------
# 4. Quotation Model
# ---------------------------------------------------------------------------
class Quotation(db.Model):
    """
    Represents a price/quantity offer made by a customer for a product.

    A quotation may receive an AI recommendation (advisory only) and,
    if accepted by the farmer, can be converted into an Order.
    """

    __tablename__ = "quotations"

    quotation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True
    )

    offered_price = db.Column(db.Float, nullable=False)       # price per unit offered by customer
    requested_quantity = db.Column(db.Float, nullable=False)

    quotation_status = db.Column(db.String(20), default="Pending", nullable=False)
    # Values: Pending / Accepted / Rejected / Expired / Withdrawn

    quotation_deadline = db.Column(db.DateTime, nullable=True)
    distance_from_farmer = db.Column(db.Float, nullable=True)  # in kilometers

    # --- AI advisory fields (denormalized summary; full detail in AIRecommendation) ---
    ai_score = db.Column(db.Float, nullable=True)
    ai_recommended = db.Column(db.Boolean, default=False, nullable=False)

    # --- Farmer's manual decision - the ONLY thing that changes order status ---
    farmer_decision = db.Column(db.String(20), nullable=True)  # Accepted / Rejected / Pending
    explanation_text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    # --- Relationships ---
    customer = db.relationship("Customer", back_populates="quotations")
    product = db.relationship("Product", back_populates="quotations")
    ai_recommendation = db.relationship(
        "AIRecommendation", back_populates="quotation", uselist=False, cascade="all, delete-orphan"
    )
    order = db.relationship(
        "Order", back_populates="quotation", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("offered_price > 0", name="ck_quotation_price_positive"),
        CheckConstraint("requested_quantity > 0", name="ck_quotation_quantity_positive"),
        CheckConstraint(
            "quotation_status IN ('Pending', 'Accepted', 'Rejected', 'Expired', 'Withdrawn')",
            name="ck_quotation_status",
        ),
    )

    def __repr__(self):
        return f"<Quotation id={self.quotation_id} product_id={self.product_id} status='{self.quotation_status}'>"


# ---------------------------------------------------------------------------
# 5. AI Recommendation Model
# ---------------------------------------------------------------------------
class AIRecommendation(db.Model):
    """
    Stores the AI-generated scoring breakdown for a single quotation.

    IMPORTANT: This model is strictly advisory. The AI recommendation score
    must NEVER be used to automatically accept, reject, or otherwise change
    a quotation's or order's status. Only a farmer's explicit action
    (Quotation.farmer_decision) can change quotation/order state.
    """

    __tablename__ = "ai_recommendations"

    recommendation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quotation_id = db.Column(
        db.Integer,
        db.ForeignKey("quotations.quotation_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one recommendation per quotation
        index=True,
    )

    # --- Individual sub-scores (0-100 scale) ---
    recommendation_score = db.Column(db.Float, nullable=False)  # overall composite (alias/summary)
    price_score = db.Column(db.Float, nullable=True)
    quantity_score = db.Column(db.Float, nullable=True)
    distance_score = db.Column(db.Float, nullable=True)
    reliability_score = db.Column(db.Float, nullable=True)
    overall_score = db.Column(db.Float, nullable=True)

    explanation = db.Column(db.Text, nullable=True)  # human-readable reasoning for transparency
    generated_time = db.Column(db.DateTime, default=utcnow, nullable=False)

    # --- Relationships ---
    quotation = db.relationship("Quotation", back_populates="ai_recommendation")

    __table_args__ = (
        CheckConstraint(
            "recommendation_score >= 0 AND recommendation_score <= 100", name="ck_ai_rec_score_range"
        ),
    )

    def __repr__(self):
        return f"<AIRecommendation id={self.recommendation_id} quotation_id={self.quotation_id} score={self.overall_score}>"


# ---------------------------------------------------------------------------
# 6. Order Model
# ---------------------------------------------------------------------------
class Order(db.Model):
    """
    Represents a confirmed order created after a farmer accepts a quotation.

    Order status transitions are driven exclusively by explicit farmer/
    system actions (never automatically by AI recommendations).
    """

    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quotation_id = db.Column(
        db.Integer,
        db.ForeignKey("quotations.quotation_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    farmer_id = db.Column(
        db.Integer, db.ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )

    total_amount = db.Column(db.Float, nullable=False)
    delivery_charge = db.Column(db.Float, default=0.0, nullable=False)

    payment_status = db.Column(db.String(20), default="Pending", nullable=False)
    # Values: Pending / Paid / Failed / Refunded

    order_status = db.Column(db.String(20), default="Requested", nullable=False)
    # Allowed values (enforced via CheckConstraint below):
    # Requested, Accepted, Rejected, Packed, Out for Delivery, Delivered, Cancelled

    order_date = db.Column(db.DateTime, default=utcnow, nullable=False)
    packed_date = db.Column(db.DateTime, nullable=True)
    shipped_date = db.Column(db.DateTime, nullable=True)
    delivered_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    # --- Relationships ---
    quotation = db.relationship("Quotation", back_populates="order")
    farmer = db.relationship("Farmer", back_populates="orders")
    customer = db.relationship("Customer", back_populates="orders")
    payment = db.relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    review = db.relationship(
        "Review", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    chats = db.relationship("Chat", back_populates="order", lazy="dynamic")

    __table_args__ = (
        CheckConstraint("total_amount > 0", name="ck_order_total_amount_positive"),
        CheckConstraint(
            "order_status IN ('Requested', 'Accepted', 'Rejected', 'Packed', "
            "'Out for Delivery', 'Delivered', 'Cancelled')",
            name="ck_order_status",
        ),
        CheckConstraint(
            "payment_status IN ('Pending', 'Paid', 'Failed', 'Refunded')",
            name="ck_order_payment_status",
        ),
    )

    def __repr__(self):
        return f"<Order id={self.order_id} status='{self.order_status}' amount={self.total_amount}>"


# ---------------------------------------------------------------------------
# 7. Payment Model
# ---------------------------------------------------------------------------
class Payment(db.Model):
    """
    Represents a payment transaction tied to a single order.
    """

    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one payment record per order
        index=True,
    )

    transaction_id = db.Column(db.String(100), nullable=True, unique=True)
    payment_method = db.Column(db.String(20), nullable=False)
    # Values: UPI / Debit Card / Credit Card / Net Banking / Cash on Delivery

    payment_status = db.Column(db.String(20), default="Pending", nullable=False)
    # Values: Pending / Success / Failed / Refunded

    payment_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=utcnow, nullable=False)

    # --- Relationships ---
    order = db.relationship("Order", back_populates="payment")

    __table_args__ = (
        CheckConstraint("payment_amount > 0", name="ck_payment_amount_positive"),
        CheckConstraint(
            "payment_method IN ('UPI', 'Debit Card', 'Credit Card', 'Net Banking', 'Cash on Delivery')",
            name="ck_payment_method",
        ),
        CheckConstraint(
            "payment_status IN ('Pending', 'Success', 'Failed', 'Refunded')",
            name="ck_payment_status",
        ),
    )

    def __repr__(self):
        return f"<Payment id={self.payment_id} order_id={self.order_id} status='{self.payment_status}'>"


# ---------------------------------------------------------------------------
# 8. Review Model
# ---------------------------------------------------------------------------
class Review(db.Model):
    """
    Represents a customer's review of a farmer, tied to a completed order.

    Only verified buyers (i.e. customers with a corresponding delivered
    Order) should be permitted to create a review — this is enforced at
    the application/service layer, and reinforced here via a unique
    constraint on order_id (one review per order).
    """

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    farmer_id = db.Column(
        db.Integer, db.ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # enforces "one review per order" -> verified-purchase-only reviews
        index=True,
    )

    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    review_text = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, default=utcnow, nullable=False)

    # --- Relationships ---
    customer = db.relationship("Customer", back_populates="reviews")
    farmer = db.relationship("Farmer", back_populates="reviews")
    order = db.relationship("Order", back_populates="review")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    @validates("rating")
    def validate_rating(self, key, value):
        """Defensive validation in addition to the DB-level CheckConstraint."""
        if not 1 <= value <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return value

    def __repr__(self):
        return f"<Review id={self.review_id} farmer_id={self.farmer_id} rating={self.rating}>"


# ---------------------------------------------------------------------------
# 9. Chat Model
# ---------------------------------------------------------------------------
class Chat(db.Model):
    """
    Represents a single chat message between a farmer and a customer,
    optionally scoped to a specific order for context.

    `sender_id` / `receiver_id` reference either a farmer or a customer.
    Since farmers and customers live in separate tables, the actual FK
    relationship is resolved via the optional sender_farmer/sender_customer
    relationships below (only one will be populated per message, determined
    by `sender_type`/`receiver_type` at the application layer).
    """

    __tablename__ = "chats"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Generic sender/receiver ids; `sender_type`/`receiver_type` disambiguate
    # whether the id refers to a farmer or a customer.
    sender_id = db.Column(db.Integer, nullable=False, index=True)
    sender_type = db.Column(db.String(10), nullable=False)   # 'farmer' or 'customer'
    receiver_id = db.Column(db.Integer, nullable=False, index=True)
    receiver_type = db.Column(db.String(10), nullable=False)  # 'farmer' or 'customer'

    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.order_id", ondelete="SET NULL"), nullable=True, index=True
    )

    message = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(255), nullable=True)  # file path / URL

    sent_time = db.Column(db.DateTime, default=utcnow, nullable=False)
    read_status = db.Column(db.Boolean, default=False, nullable=False)

    # --- Optional typed relationships for convenience querying ---
    # (Only meaningful when sender_type/receiver_type match 'farmer'/'customer';
    #  these are best-effort convenience joins, not enforced FKs, since sender_id
    #  is polymorphic across two tables.)
    order = db.relationship("Order", back_populates="chats")

    sender_farmer = db.relationship(
        "Farmer",
        primaryjoin="and_(foreign(Chat.sender_id)==Farmer.farmer_id, Chat.sender_type=='farmer')",
        back_populates="sent_chats",
        viewonly=True,
    )
    sender_customer = db.relationship(
        "Customer",
        primaryjoin="and_(foreign(Chat.sender_id)==Customer.customer_id, Chat.sender_type=='customer')",
        back_populates="sent_chats",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("sender_type IN ('farmer', 'customer')", name="ck_chat_sender_type"),
        CheckConstraint("receiver_type IN ('farmer', 'customer')", name="ck_chat_receiver_type"),
    )

    def __repr__(self):
        return f"<Chat id={self.message_id} from={self.sender_type}:{self.sender_id} to={self.receiver_type}:{self.receiver_id}>"


# ---------------------------------------------------------------------------
# 10. Notification Model
# ---------------------------------------------------------------------------
class Notification(db.Model):
    """
    Represents an in-app notification sent to either a farmer or a customer.

    `user_id` is polymorphic and disambiguated by `user_type`
    ('farmer' or 'customer'), similar to the Chat model's sender/receiver.
    """

    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, nullable=False, index=True)
    user_type = db.Column(db.String(10), nullable=False)  # 'farmer' or 'customer'

    notification_title = db.Column(db.String(150), nullable=False)
    notification_message = db.Column(db.Text, nullable=True)

    notification_type = db.Column(db.String(40), nullable=False)
    # Values: Quotation Received / Order Accepted / Payment Success /
    #         Delivery Update / AI Recommendation Ready

    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("user_type IN ('farmer', 'customer')", name="ck_notification_user_type"),
        CheckConstraint(
            "notification_type IN ('Quotation Received', 'Order Accepted', 'Payment Success', "
            "'Delivery Update', 'AI Recommendation Ready')",
            name="ck_notification_type",
        ),
    )

    def __repr__(self):
        return f"<Notification id={self.notification_id} type='{self.notification_type}' user={self.user_type}:{self.user_id}>"


# ---------------------------------------------------------------------------
# 11. Buyer Reliability Model
# ---------------------------------------------------------------------------
class BuyerReliability(db.Model):
    """
    Stores the detailed reliability breakdown for a customer/buyer.

    `reliability_score` is automatically recalculated (see
    `recalculate_score`) whenever order outcomes or ratings change,
    and is intended to be kept in sync with Customer.reliability_score.
    """

    __tablename__ = "buyer_reliability"

    reliability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    successful_orders = db.Column(db.Integer, default=0, nullable=False)
    cancelled_orders = db.Column(db.Integer, default=0, nullable=False)
    return_percentage = db.Column(db.Float, default=0.0, nullable=False)
    average_rating = db.Column(db.Float, default=0.0, nullable=False)
    reliability_score = db.Column(db.Float, default=50.0, nullable=False)

    # --- Relationships ---
    customer = db.relationship("Customer", back_populates="reliability_detail")

    __table_args__ = (
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 100", name="ck_buyer_reliability_range"
        ),
        CheckConstraint(
            "return_percentage >= 0 AND return_percentage <= 100", name="ck_buyer_return_pct_range"
        ),
    )

    def recalculate_score(self):
        """
        Automatically recalculate the reliability score (0-100) using a
        simple weighted formula. Intended to be called by application/
        service-layer logic after any order or review update, e.g.:

            reliability.recalculate_score()
            db.session.commit()

        Weighting (tunable):
            - 50% success rate (successful / total orders)
            - 30% average rating (normalized to 0-100)
            - 20% inverse of return/cancellation percentage
        """
        total = self.successful_orders + self.cancelled_orders
        success_rate = (self.successful_orders / total * 100) if total > 0 else 50.0
        rating_component = (self.average_rating / 5) * 100 if self.average_rating else 50.0
        cancellation_penalty = self.return_percentage

        score = (0.5 * success_rate) + (0.3 * rating_component) + (0.2 * (100 - cancellation_penalty))
        self.reliability_score = max(0.0, min(100.0, round(score, 2)))
        return self.reliability_score

    def __repr__(self):
        return f"<BuyerReliability customer_id={self.customer_id} score={self.reliability_score}>"


# ---------------------------------------------------------------------------
# 12. Voice Assistant Log Model
# ---------------------------------------------------------------------------
class VoiceAssistantLog(db.Model):
    """
    Logs each voice-assistant command issued by a user (farmer or customer),
    primarily for auditing, debugging, and improving language/command
    recognition (e.g. for Tamil-language voice support).
    """

    __tablename__ = "voice_assistant_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, nullable=False, index=True)
    user_type = db.Column(db.String(10), nullable=True)  # 'farmer' or 'customer'

    command = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default="en", nullable=False)  # e.g. 'ta' for Tamil, 'en'

    execution_status = db.Column(db.String(20), default="Success", nullable=False)
    # Values: Success / Failed / Not Recognized

    timestamp = db.Column(db.DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "execution_status IN ('Success', 'Failed', 'Not Recognized')",
            name="ck_voice_log_execution_status",
        ),
    )

    def __repr__(self):
        return f"<VoiceAssistantLog id={self.log_id} user={self.user_type}:{self.user_id} status='{self.execution_status}'>"


# ---------------------------------------------------------------------------
# Extra integrity constraints (applied at class-definition time above via
# __table_args__). Summary of key business rules enforced at the DB level:
#
#   - Farmer.email / Farmer.mobile_number / Farmer.aadhaar_number -> unique
#   - Customer.email / Customer.mobile_number -> unique
#   - Review.rating -> between 1 and 5 (CheckConstraint + validator)
#   - Product.base_price -> > 0
#   - Quotation.offered_price -> > 0
#   - Product.available_quantity -> >= 0
#   - Quotation.requested_quantity -> > 0
#   - BuyerReliability.reliability_score / Customer.reliability_score -> 0-100
#   - AI recommendations (AIRecommendation) are purely advisory: no code
#     path in this schema allows an AI score to write to
#     Quotation.farmer_decision or Order.order_status directly. All status
#     transitions must originate from explicit farmer/customer/service
#     actions in the application layer.
# ---------------------------------------------------------------------------
