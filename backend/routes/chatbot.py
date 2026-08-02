"""
chatbot.py
==========

AgriConnect Farmer-Buyer Communication Assistant.

Purpose:
    - Remove middleman
    - Connect farmers and buyers directly
    - Assist marketplace conversations
    - Support negotiation and communication

Features:
    - Farmer-buyer chat
    - Message history
    - AI communication assistance
    - Future Tamil voice integration
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ChatHistory

from backend.schemas import ChatRequest

from backend.auth import get_current_user



router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)



# ==========================================
# Marketplace Communication Assistant
# ==========================================

def generate_chat_assistance(message: str):

    """
    Basic marketplace assistant.

    Future integration:
        - LLM model
        - Tamil language model
        - Voice assistant
    """


    msg = message.lower()



    if "price" in msg or "rate" in msg:

        return (
            "You can discuss price with the buyer. "
            "Confirm quantity, quality requirements, "
            "delivery location and payment terms."
        )


    elif "quantity" in msg:

        return (
            "Please confirm required quantity "
            "before finalizing the agreement."
        )


    elif "payment" in msg:

        return (
            "Confirm payment method and payment timeline "
            "before completing the transaction."
        )


    elif "delivery" in msg:

        return (
            "Discuss delivery location, transport "
            "responsibility and expected delivery date."
        )


    else:

        return (
            "You can directly communicate with the buyer. "
            "Discuss product details, quantity, price, "
            "delivery and payment terms."
        )



# ==========================================
# Start Conversation
# ==========================================

@router.post("/")
def create_chat(
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer or buyer starts communication.
    """


    if current_user.role not in [
        "farmer",
        "customer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Only farmers and customers can chat"
        )



    response = generate_chat_assistance(
        chat_data.message
    )



    chat = ChatHistory(

        user_id=current_user.id,

        user_message=chat_data.message,

        bot_response=response

    )



    db.add(chat)

    db.commit()

    db.refresh(chat)



    return {

        "message":
        "Message processed successfully",

        "chat_id":
        chat.id,

        "user_message":
        chat.user_message,

        "assistant_response":
        response

    }
# ==========================================
# Create Farmer-Buyer Conversation
# ==========================================

@router.post("/conversation")
def create_conversation(
    buyer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Creates direct communication channel
    between farmer and buyer.
    """


    if current_user.role not in [
        "farmer",
        "customer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Only farmers and customers can create conversations"
        )



    conversation = ChatHistory(

        sender_id=current_user.id,

        receiver_id=buyer_id,

        message_type="text",

        message="Conversation started"

    )



    db.add(conversation)

    db.commit()

    db.refresh(conversation)



    return {

        "message":
        "Conversation created",

        "conversation_id":
        conversation.id

    }



# ==========================================
# Send Direct Message
# ==========================================

@router.post("/conversation/{conversation_id}/message")
def send_message(
    conversation_id: int,
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer and buyer exchange messages.
    """


    if current_user.role not in [
        "farmer",
        "customer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Invalid user"
        )



    message = ChatHistory(

        conversation_id=conversation_id,

        sender_id=current_user.id,

        message=chat_data.message,

        message_type="text"

    )



    db.add(message)

    db.commit()

    db.refresh(message)



    return {

        "message":
        "Message sent",

        "message_id":
        message.id

    }



# ==========================================
# View Inbox
# ==========================================

@router.get("/inbox")
def chat_inbox(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Shows user's active conversations.
    """


    conversations = db.query(ChatHistory).filter(
        (
            ChatHistory.sender_id == current_user.id
        )
        |
        (
            ChatHistory.receiver_id == current_user.id
        )
    ).order_by(
        ChatHistory.created_at.desc()
    ).all()



    result = []


    for chat in conversations:

        result.append({

            "conversation_id":
            chat.conversation_id,

            "sender_id":
            chat.sender_id,

            "receiver_id":
            chat.receiver_id,

            "last_message":
            chat.message,

            "time":
            chat.created_at

        })



    return {

        "total":
        len(result),

        "conversations":
        result

    }



# ==========================================
# View Conversation Messages
# ==========================================

@router.get("/conversation/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    messages = db.query(ChatHistory).filter(
        ChatHistory.conversation_id ==
        conversation_id
    ).order_by(
        ChatHistory.created_at.asc()
    ).all()



    if not messages:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )



    result = []



    for message in messages:

        result.append({

            "sender_id":
            message.sender_id,

            "message":
            message.message,

            "type":
            message.message_type,

            "time":
            message.created_at

        })



    return {

        "conversation_id":
        conversation_id,

        "messages":
        result

    }
# ==========================================
# Language Detection
# ==========================================

def detect_language(message: str):

    """
    Detects user language.

    Future integration:
        - AI language detector
        - Tamil NLP model
    """


    tamil_chars = 0


    for char in message:

        if "\u0B80" <= char <= "\u0BFF":

            tamil_chars += 1



    if tamil_chars > 0:

        return "tamil"


    return "english"



# ==========================================
# Translate Farmer-Buyer Message
# ==========================================

def translate_message(
    message: str,
    target_language: str
):

    """
    Translation layer.

    Future:
        - Google Translate API
        - Indic NLP
        - Custom Tamil model
    """


    # Placeholder response

    return message



# ==========================================
# Send Multilingual Message
# ==========================================

@router.post(
    "/conversation/{conversation_id}/multilingual"
)
def send_multilingual_message(
    conversation_id: int,
    chat_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Handles Tamil/English messages
    between farmer and buyer.
    """


    language = detect_language(
        chat_data.message
    )



    translated_text = translate_message(
        chat_data.message,
        "english"
    )



    message = ChatHistory(

        conversation_id=conversation_id,

        sender_id=current_user.id,

        message=translated_text,

        original_message=chat_data.message,

        language=language,

        message_type="text"

    )



    db.add(message)

    db.commit()

    db.refresh(message)



    return {

        "message":
        "Multilingual message sent",

        "detected_language":
        language,

        "original":
        chat_data.message,

        "translated":
        translated_text

    }



# ==========================================
# Voice Message Upload
# ==========================================

@router.post(
    "/conversation/{conversation_id}/voice"
)
def send_voice_message(
    conversation_id: int,
    audio_file: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Voice communication between farmer
    and buyer.

    Future integration:
        - Whisper speech recognition
        - Tamil speech model
        - Text-to-speech
    """



    # Placeholder transcription

    transcript = (
        "Voice message transcription will "
        "be generated here"
    )



    message = ChatHistory(

        conversation_id=conversation_id,

        sender_id=current_user.id,

        message=transcript,

        message_type="voice",

        audio_path=audio_file

    )



    db.add(message)

    db.commit()

    db.refresh(message)



    return {

        "message":
        "Voice message received",

        "transcript":
        transcript,

        "message_id":
        message.id

    }



# ==========================================
# Voice Response Generator
# ==========================================

def generate_voice_response(
    text: str,
    language="tamil"
):

    """
    Converts chatbot response into voice.

    Future:
        - Text To Speech API
        - Tamil voice model
    """


    return {

        "text":
        text,

        "audio":
        "generated_audio_file_path"

    }



# ==========================================
# Convert Message To Voice
# ==========================================

@router.post(
    "/voice-response"
)
def voice_response(
    text: str,
    language: str = "tamil"
):


    response = generate_voice_response(
        text,
        language
    )


    return {

        "language":
        language,

        "response":
        response

    }
# ==========================================
# Quotation Discussion Assistant
# ==========================================

def quotation_assistance(message: str):

    """
    Helps users during quotation discussion.

    Future integration:
        - LLM negotiation model
        - Market intelligence service
    """


    msg = message.lower()



    if "price" in msg or "rate" in msg:

        return {

            "advice":

            [
                "Confirm product quality requirements",
                "Discuss quantity before finalizing price",
                "Compare payment terms"
            ]

        }



    elif "payment" in msg:

        return {

            "advice":

            [
                "Confirm payment method",
                "Confirm payment timeline",
                "Avoid unclear payment agreements"
            ]

        }



    elif "delivery" in msg:

        return {

            "advice":

            [
                "Confirm delivery location",
                "Decide transport responsibility",
                "Confirm delivery date"
            ]

        }



    else:

        return {

            "advice":

            [
                "Confirm product details",
                "Confirm quantity",
                "Confirm price",
                "Confirm payment",
                "Confirm delivery"
            ]

        }



# ==========================================
# Analyze Quotation Conversation
# ==========================================

@router.post(
    "/quotation-assistant"
)
def quotation_chat_assistant(
    chat_data: ChatRequest,
    current_user = Depends(get_current_user)
):

    """
    Gives transaction guidance during
    farmer-buyer negotiation.
    """


    if current_user.role not in [
        "farmer",
        "customer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Only marketplace users allowed"
        )



    result = quotation_assistance(
        chat_data.message
    )



    return {

        "user_message":
        chat_data.message,

        "assistant":
        result

    }



# ==========================================
# Buyer Requirement Checklist
# ==========================================

@router.get("/buyer-checklist")
def buyer_requirement_checklist():

    """
    Checklist before buyer confirms order.
    """


    return {

        "requirements":

        [

            "Product name",

            "Required quantity",

            "Quality specification",

            "Delivery location",

            "Required delivery date",

            "Payment method",

            "Special requirements"

        ]

    }



# ==========================================
# Farmer Negotiation Checklist
# ==========================================

@router.get("/farmer-negotiation-checklist")
def farmer_negotiation_checklist():

    """
    Things farmer should confirm
    before accepting buyer offer.
    """


    return {

        "check_before_accepting":

        [

            "Buyer identity verification",

            "Final price",

            "Quantity confirmation",

            "Payment timeline",

            "Transport responsibility",

            "Delivery conditions"

        ]

    }



# ==========================================
# Smart Conversation Summary
# ==========================================

@router.get(
    "/conversation/{conversation_id}/summary"
)
def conversation_summary(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    messages = db.query(ChatHistory).filter(
        ChatHistory.conversation_id ==
        conversation_id
    ).all()



    if not messages:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )



    summary = {

        "product_discussed": None,

        "quantity": None,

        "price": None,

        "payment_discussed": False,

        "delivery_discussed": False

    }



    for message in messages:

        text = message.message.lower()


        if "kg" in text or "ton" in text:

            summary["quantity"] = message.message


        if "₹" in text or "price" in text:

            summary["price"] = message.message


        if "payment" in text:

            summary["payment_discussed"] = True


        if "delivery" in text:

            summary["delivery_discussed"] = True



    return {

        "conversation_id":
        conversation_id,

        "summary":
        summary

    }
# ==========================================
# Transaction Safety Assistant
# ==========================================

def transaction_safety_check(message: str):

    """
    Identifies risky transaction situations.

    Future:
        - Fraud detection model
        - Buyer verification system
    """


    warnings = []



    msg = message.lower()



    if "before delivery" in msg:

        warnings.append(
            "Confirm payment terms before delivering products."
        )



    if "advance" not in msg and "payment" not in msg:

        warnings.append(
            "Confirm payment agreement clearly."
        )



    if "unknown" in msg:

        warnings.append(
            "Verify buyer identity before transaction."
        )



    if not warnings:

        warnings.append(
            "No major communication risks detected."
        )



    return warnings



# ==========================================
# Transaction Safety Check API
# ==========================================

@router.post("/safety-check")
def safety_check(
    chat_data: ChatRequest,
    current_user = Depends(get_current_user)
):


    if current_user.role not in [
        "farmer",
        "customer"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Only marketplace users allowed"
        )



    result = transaction_safety_check(
        chat_data.message
    )



    return {

        "message":
        chat_data.message,

        "safety_notes":
        result

    }



# ==========================================
# Chat Analytics
# ==========================================

@router.get("/analytics")
def chat_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    messages = db.query(ChatHistory).filter(
        ChatHistory.sender_id ==
        current_user.id
    ).all()



    total_messages = len(messages)



    voice_messages = len([
        message
        for message in messages
        if message.message_type == "voice"
    ])



    text_messages = len([
        message
        for message in messages
        if message.message_type == "text"
    ])



    return {

        "user_id":
        current_user.id,

        "total_messages":
        total_messages,

        "text_messages":
        text_messages,

        "voice_messages":
        voice_messages

    }



# ==========================================
# Notification Hook
# ==========================================

def send_chat_notification(
    receiver_id,
    message
):

    """
    Future connection:

        notification.py

    Examples:
        - New buyer message
        - New quotation discussion
        - Payment confirmation
    """


    return {

        "receiver":
        receiver_id,

        "notification":
        message

    }



# ==========================================
# Notify New Message
# ==========================================

@router.post(
    "/conversation/{conversation_id}/notify"
)
def notify_message(
    conversation_id: int,
    receiver_id: int,
    message: str
):


    notification = send_chat_notification(
        receiver_id,
        message
    )


    return {

        "conversation_id":
        conversation_id,

        "notification":
        notification

    }



# ==========================================
# Chatbot Module Status
# ==========================================

@router.get("/")
def chatbot_home():

    return {

        "module":
        "Farmer Buyer Communication Assistant",

        "status":
        "active",

        "purpose":
        "Direct connection between farmers and buyers",

        "features":

        [

            "Direct Farmer-Buyer Chat",

            "Tamil Language Support",

            "Voice Communication",

            "Translation Support",

            "Quotation Discussion",

            "Negotiation Assistance",

            "Transaction Safety",

            "Conversation History"

        ]

    }