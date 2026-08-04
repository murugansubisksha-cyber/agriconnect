"""
chatbot.py
==========

Farmer <-> Buyer direct-messaging routes for AgriConnect (Flask).

Purpose:
    - Remove the middleman: let farmers and customers message each
      other directly, optionally scoped to a specific order.

Features:
    - Send a message
    - View a conversation thread with a specific other user
    - Inbox: list conversation partners with their last message
    - Mark messages as read
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import or_

from database import db
from models import Chat, Customer, Farmer

chatbot_bp = Blueprint(
    "chatbot",
    __name__,
    url_prefix="/api/chat"
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


def serialize_chat(chat):
    return {
        "message_id": chat.message_id,
        "sender_id": chat.sender_id,
        "sender_type": chat.sender_type,
        "receiver_id": chat.receiver_id,
        "receiver_type": chat.receiver_type,
        "order_id": chat.order_id,
        "message": chat.message,
        "attachment": chat.attachment,
        "sent_time": chat.sent_time.isoformat() if chat.sent_time else None,
        "read_status": chat.read_status,
    }


def other_type(user_type):
    return "customer" if user_type == "farmer" else "farmer"


# ==========================================================
# Send Message
# ==========================================================

@chatbot_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    data = request.get_json(silent=True) or {}

    receiver_id = data.get("receiver_id")
    message = data.get("message")

    if not receiver_id or not message:
        return jsonify({
            "success": False,
            "message": "receiver_id and message are required."
        }), 400

    receiver_type = other_type(user_type)

    if receiver_type == "farmer":
        receiver_exists = Farmer.query.filter_by(farmer_id=receiver_id).first()
    else:
        receiver_exists = Customer.query.filter_by(customer_id=receiver_id).first()

    if receiver_exists is None:
        return jsonify({"success": False, "message": "Recipient not found."}), 404

    sender_id = user.farmer_id if user_type == "farmer" else user.customer_id

    chat = Chat(
        sender_id=sender_id,
        sender_type=user_type,
        receiver_id=receiver_id,
        receiver_type=receiver_type,
        order_id=data.get("order_id"),
        message=message,
        attachment=data.get("attachment"),
    )

    db.session.add(chat)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Message sent.",
        "chat": serialize_chat(chat)
    }), 201


# ==========================================================
# Conversation Thread With a Specific Other User
# ==========================================================

@chatbot_bp.route("/conversation/<int:other_id>", methods=["GET"])
@jwt_required()
def conversation(other_id):
    """
    Full message thread between the logged-in user and one other
    user (the other role is inferred automatically -- a farmer
    always talks to customers and vice versa).
    """

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    my_id = user.farmer_id if user_type == "farmer" else user.customer_id
    other_role = other_type(user_type)

    messages = (
        Chat.query
        .filter(
            or_(
                (Chat.sender_id == my_id) & (Chat.sender_type == user_type)
                & (Chat.receiver_id == other_id) & (Chat.receiver_type == other_role),
                (Chat.sender_id == other_id) & (Chat.sender_type == other_role)
                & (Chat.receiver_id == my_id) & (Chat.receiver_type == user_type),
            )
        )
        .order_by(Chat.sent_time.asc())
        .all()
    )

    # Mark incoming messages in this thread as read
    for m in messages:
        if m.receiver_id == my_id and m.receiver_type == user_type and not m.read_status:
            m.read_status = True
    db.session.commit()

    return jsonify({
        "success": True,
        "count": len(messages),
        "messages": [serialize_chat(m) for m in messages]
    }), 200


# ==========================================================
# Inbox -- List of Conversation Partners
# ==========================================================

@chatbot_bp.route("/inbox", methods=["GET"])
@jwt_required()
def inbox():

    user_type, user = current_user()

    if user is None:
        return jsonify({"success": False, "message": "Unauthorized."}), 403

    my_id = user.farmer_id if user_type == "farmer" else user.customer_id

    messages = (
        Chat.query
        .filter(
            or_(
                (Chat.sender_id == my_id) & (Chat.sender_type == user_type),
                (Chat.receiver_id == my_id) & (Chat.receiver_type == user_type),
            )
        )
        .order_by(Chat.sent_time.desc())
        .all()
    )

    conversations = {}
    for m in messages:
        if m.sender_id == my_id and m.sender_type == user_type:
            partner_id = m.receiver_id
        else:
            partner_id = m.sender_id

        if partner_id not in conversations:
            unread = sum(
                1 for x in messages
                if x.sender_id == partner_id
                and x.receiver_id == my_id
                and not x.read_status
            )
            conversations[partner_id] = {
                "partner_id": partner_id,
                "last_message": m.message,
                "last_message_time": m.sent_time.isoformat() if m.sent_time else None,
                "unread_count": unread,
            }

    return jsonify({
        "success": True,
        "count": len(conversations),
        "conversations": list(conversations.values())
    }), 200


# ==========================================================
# Blueprint Health Check
# ==========================================================

@chatbot_bp.route("/status/ping", methods=["GET"])
def chatbot_home():
    return jsonify({
        "success": True,
        "blueprint": "chatbot",
        "status": "active"
    }), 200