"""
payment.py
==========

Payment management routes for AgriConnect.

Features:
    - Create payment record
    - View payment details
    - Update payment status
    - Track transaction history
    - Connect with orders
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Payment, Order
from backend.schemas import (
    PaymentCreate,
    PaymentStatusUpdate
)

from backend.auth import get_current_user


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)



# ==========================================
# Create Payment
# ==========================================

@router.post("/")
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer creates payment for an order
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can make payments"
        )


    order = db.query(Order).filter(
        Order.id == payment_data.order_id
    ).first()


    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    if order.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="This order does not belong to you"
        )


    payment = Payment(

        order_id = order.id,

        customer_id = current_user.id,

        amount = payment_data.amount,

        payment_method = payment_data.payment_method,

        payment_status = "pending"

    )


    db.add(payment)

    db.commit()

    db.refresh(payment)


    return {

        "message": "Payment initiated successfully",

        "payment_id": payment.id,

        "order_id": order.id,

        "status": payment.payment_status

    }
# ==========================================
# Get Payment Details
# ==========================================

@router.get("/{payment_id}")
def get_payment_details(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()


    # Customer can view own payment
    if current_user.role == "customer":

        if payment.customer_id != current_user.id:

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )


    # Farmer can view payments for their orders
    elif current_user.role == "farmer":

        if order.farmer_id != current_user.id:

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )


    return {

        "payment_id": payment.id,

        "order_id": payment.order_id,

        "amount": payment.amount,

        "payment_method": payment.payment_method,

        "payment_status": payment.payment_status,

        "created_at": payment.created_at

    }



# ==========================================
# Customer Payment History
# ==========================================

@router.get("/customer/history")
def customer_payment_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can access payment history"
        )


    payments = db.query(Payment).filter(
        Payment.customer_id == current_user.id
    ).order_by(
        Payment.created_at.desc()
    ).all()


    history = []


    for payment in payments:

        history.append({

            "payment_id": payment.id,

            "order_id": payment.order_id,

            "amount": payment.amount,

            "method": payment.payment_method,

            "status": payment.payment_status,

            "date": payment.created_at

        })


    return {

        "total_payments": len(history),

        "payments": history

    }



# ==========================================
# Farmer Payment Summary
# ==========================================

@router.get("/farmer/summary")
def farmer_payment_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can view payment summary"
        )


    orders = db.query(Order).filter(
        Order.farmer_id == current_user.id
    ).all()


    order_ids = [
        order.id
        for order in orders
    ]


    payments = db.query(Payment).filter(
        Payment.order_id.in_(order_ids)
    ).all()


    total_amount = sum(
        payment.amount
        for payment in payments
        if payment.payment_status == "paid"
    )


    return {

        "total_orders": len(order_ids),

        "completed_payments": len(payments),

        "earned_amount": total_amount

    }
# ==========================================
# Update Payment Status
# ==========================================

@router.put("/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status_data: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Updates payment status after transaction response.

    Status:
        pending
        paid
        failed
    """


    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can update payment"
        )


    if payment.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot modify this payment"
        )


    allowed_status = [
        "pending",
        "paid",
        "failed"
    ]


    if status_data.status not in allowed_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )


    payment.payment_status = status_data.status


    db.commit()

    db.refresh(payment)


    return {

        "message": "Payment status updated successfully",

        "payment_id": payment.id,

        "status": payment.payment_status

    }



# ==========================================
# Verify Payment
# ==========================================

@router.get("/{payment_id}/verify")
def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    if payment.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    if payment.payment_status == "paid":

        message = "Payment completed successfully"


    elif payment.payment_status == "failed":

        message = "Payment failed"


    else:

        message = "Payment is still pending"



    return {

        "payment_id": payment.id,

        "status": payment.payment_status,

        "message": message

    }



# ==========================================
# Refund Request
# ==========================================

@router.post("/{payment_id}/refund")
def request_refund(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    if payment.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot request refund"
        )


    if payment.payment_status != "paid":

        raise HTTPException(
            status_code=400,
            detail="Refund available only for completed payments"
        )


    payment.payment_status = "refund_requested"


    db.commit()


    return {

        "message": "Refund request submitted",

        "payment_id": payment.id,

        "status": payment.payment_status

    }
# ==========================================
# Payment Analytics
# ==========================================

@router.get("/analytics/summary")
def payment_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Gives payment statistics.

    Farmer:
        - Earnings from orders

    Customer:
        - Spending summary
    """


    if current_user.role == "farmer":

        orders = db.query(Order).filter(
            Order.farmer_id == current_user.id
        ).all()


        order_ids = [
            order.id
            for order in orders
        ]


        payments = db.query(Payment).filter(
            Payment.order_id.in_(order_ids)
        ).all()


    elif current_user.role == "customer":

        payments = db.query(Payment).filter(
            Payment.customer_id == current_user.id
        ).all()


    else:

        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )


    total_transactions = len(payments)


    completed = len([
        payment
        for payment in payments
        if payment.payment_status == "paid"
    ])


    pending = len([
        payment
        for payment in payments
        if payment.payment_status == "pending"
    ])


    total_amount = sum(
        payment.amount
        for payment in payments
        if payment.payment_status == "paid"
    )


    return {

        "total_transactions": total_transactions,

        "completed_transactions": completed,

        "pending_transactions": pending,

        "total_amount": total_amount

    }



# ==========================================
# Filter Payments
# ==========================================

@router.get("/filter")
def filter_payments(
    status: str = None,
    method: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    query = db.query(Payment)


    if current_user.role == "customer":

        query = query.filter(
            Payment.customer_id == current_user.id
        )


    elif current_user.role == "farmer":

        farmer_orders = db.query(Order).filter(
            Order.farmer_id == current_user.id
        ).all()


        order_ids = [
            order.id
            for order in farmer_orders
        ]


        query = query.filter(
            Payment.order_id.in_(order_ids)
        )


    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    if status:

        query = query.filter(
            Payment.payment_status == status
        )


    if method:

        query = query.filter(
            Payment.payment_method == method
        )


    payments = query.all()


    result = []


    for payment in payments:

        result.append({

            "payment_id": payment.id,

            "order_id": payment.order_id,

            "amount": payment.amount,

            "method": payment.payment_method,

            "status": payment.payment_status

        })


    return {

        "count": len(result),

        "payments": result

    }



# ==========================================
# Transaction Report
# ==========================================

@router.get("/report")
def transaction_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    payments = db.query(Payment).filter(
        Payment.customer_id == current_user.id
    ).all()


    report = []


    for payment in payments:

        report.append({

            "transaction_id": payment.id,

            "order_id": payment.order_id,

            "amount": payment.amount,

            "status": payment.payment_status,

            "date": payment.created_at

        })


    return {

        "generated_for": current_user.id,

        "transactions": report

    }
# ==========================================
# Payment Gateway Initialization
# ==========================================

@router.post("/{payment_id}/gateway")
def initiate_gateway_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Placeholder for payment gateway integration.

    Future integration:
        - Razorpay
        - Stripe
        - PayPal

    Currently creates a transaction reference.
    """


    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    if payment.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    transaction_reference = (
        f"AGRICONNECT_TXN_{payment.id}"
    )


    return {

        "message": "Payment gateway initialized",

        "payment_id": payment.id,

        "transaction_reference":
            transaction_reference,

        "amount": payment.amount,

        "status": "pending"

    }



# ==========================================
# Payment Success Notification
# ==========================================

@router.post("/{payment_id}/success")
def payment_success(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    if payment.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    payment.payment_status = "paid"


    db.commit()


    # Notification system hook
    # Future:
    # notify farmer about successful payment


    return {

        "message":
        "Payment completed successfully",

        "payment_id":
        payment.id,

        "status":
        payment.payment_status

    }



# ==========================================
# Payment Failure Handler
# ==========================================

@router.post("/{payment_id}/failed")
def payment_failed(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    payment.payment_status = "failed"


    db.commit()


    return {

        "message":
        "Payment marked as failed",

        "payment_id":
        payment.id,

        "status":
        payment.payment_status

    }



# ==========================================
# Payment Module Status
# ==========================================

@router.get("/")
def payment_home():

    return {

        "module":
        "Payment Management",

        "status":
        "active",

        "features": [

            "Create Payment",

            "Track Transactions",

            "Payment Verification",

            "Refund Requests",

            "Revenue Analytics",

            "Gateway Ready"

        ]

    }