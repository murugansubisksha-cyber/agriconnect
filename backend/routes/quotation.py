"""
quotation.py
============

Quotation management routes for AgriConnect.

Features:
    - Farmer creates quotation
    - Customer receives quotation
    - Accept/reject quotation
    - Track quotation status
    - Connect with orders
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Quotation, Product
from backend.schemas import (
    QuotationCreate,
    QuotationStatusUpdate
)

from backend.auth import get_current_user



router = APIRouter(
    prefix="/quotations",
    tags=["Quotations"]
)



# ==========================================
# Create Quotation (Farmer)
# ==========================================

@router.post("/")
def create_quotation(
    quotation_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer sends price quotation
    to customer for a product
    """


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can create quotations"
        )


    product = db.query(Product).filter(
        Product.id == quotation_data.product_id
    ).first()


    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    quotation = Quotation(

        farmer_id=current_user.id,

        customer_id=quotation_data.customer_id,

        product_id=quotation_data.product_id,

        quantity=quotation_data.quantity,

        offered_price=quotation_data.offered_price,

        message=quotation_data.message,

        status="pending"

    )


    db.add(quotation)

    db.commit()

    db.refresh(quotation)



    return {

        "message":
        "Quotation created successfully",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }
# ==========================================
# Customer View Received Quotations
# ==========================================

@router.get("/customer/inbox")
def customer_quotation_inbox(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer views quotations
    received from farmers
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can view quotations"
        )


    quotations = db.query(Quotation).filter(
        Quotation.customer_id == current_user.id
    ).order_by(
        Quotation.created_at.desc()
    ).all()



    result = []


    for quotation in quotations:

        result.append({

            "quotation_id": quotation.id,

            "farmer_id": quotation.farmer_id,

            "product_id": quotation.product_id,

            "quantity": quotation.quantity,

            "offered_price": quotation.offered_price,

            "message": quotation.message,

            "status": quotation.status,

            "created_at": quotation.created_at

        })


    return {

        "total":
        len(result),

        "quotations":
        result

    }



# ==========================================
# Farmer Sent Quotations History
# ==========================================

@router.get("/farmer/history")
def farmer_quotation_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can view quotation history"
        )


    quotations = db.query(Quotation).filter(
        Quotation.farmer_id == current_user.id
    ).order_by(
        Quotation.created_at.desc()
    ).all()



    history = []


    for quotation in quotations:

        history.append({

            "quotation_id":
            quotation.id,

            "customer_id":
            quotation.customer_id,

            "product_id":
            quotation.product_id,

            "price":
            quotation.offered_price,

            "quantity":
            quotation.quantity,

            "status":
            quotation.status

        })



    return {

        "total":
        len(history),

        "quotations":
        history

    }



# ==========================================
# View Single Quotation
# ==========================================

@router.get("/{quotation_id}")
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()



    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )



    if (
        quotation.customer_id != current_user.id
        and
        quotation.farmer_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    return {

        "quotation_id":
        quotation.id,

        "farmer_id":
        quotation.farmer_id,

        "customer_id":
        quotation.customer_id,

        "product_id":
        quotation.product_id,

        "quantity":
        quotation.quantity,

        "offered_price":
        quotation.offered_price,

        "message":
        quotation.message,

        "status":
        quotation.status

    }
# ==========================================
# Customer Accept Quotation
# ==========================================

@router.put("/{quotation_id}/accept")
def accept_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer accepts farmer quotation
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can accept quotations"
        )


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()


    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )


    if quotation.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="This quotation is not for you"
        )


    if quotation.status != "pending":

        raise HTTPException(
            status_code=400,
            detail="Quotation already processed"
        )


    quotation.status = "accepted"


    db.commit()

    db.refresh(quotation)


    return {

        "message":
        "Quotation accepted",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }



# ==========================================
# Customer Reject Quotation
# ==========================================

@router.put("/{quotation_id}/reject")
def reject_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can reject quotations"
        )


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()



    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )



    if quotation.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    quotation.status = "rejected"


    db.commit()



    return {

        "message":
        "Quotation rejected",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }



# ==========================================
# Farmer Update Quotation
# ==========================================

@router.put("/{quotation_id}")
def update_quotation(
    quotation_id: int,
    quotation_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer modifies quotation price,
    quantity or message.
    """


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can update quotations"
        )


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()



    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )



    if quotation.farmer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot modify this quotation"
        )



    if quotation.status != "pending":

        raise HTTPException(
            status_code=400,
            detail="Cannot edit processed quotation"
        )



    quotation.quantity = quotation_data.quantity

    quotation.offered_price = quotation_data.offered_price

    quotation.message = quotation_data.message


    db.commit()

    db.refresh(quotation)



    return {

        "message":
        "Quotation updated successfully",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }
# ==========================================
# Customer Counter Offer
# ==========================================

@router.put("/{quotation_id}/counter")
def counter_offer(
    quotation_id: int,
    quotation_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer sends a counter price
    to farmer for negotiation.
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can send counter offers"
        )


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()


    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )


    if quotation.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    if quotation.status != "pending":

        raise HTTPException(
            status_code=400,
            detail="Negotiation closed"
        )


    quotation.offered_price = (
        quotation_data.offered_price
    )

    quotation.quantity = (
        quotation_data.quantity
    )

    quotation.message = (
        quotation_data.message
    )

    quotation.status = "negotiation"


    db.commit()

    db.refresh(quotation)


    return {

        "message":
        "Counter offer sent",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }



# ==========================================
# Farmer Accept Negotiation
# ==========================================

@router.put("/{quotation_id}/approve")
def approve_negotiation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer approves negotiated quotation.
    """


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can approve"
        )


    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()


    if not quotation:

        raise HTTPException(
            status_code=404,
            detail="Quotation not found"
        )


    if quotation.farmer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


    if quotation.status != "negotiation":

        raise HTTPException(
            status_code=400,
            detail="No negotiation pending"
        )


    quotation.status = "accepted"


    db.commit()


    return {

        "message":
        "Negotiation approved",

        "quotation_id":
        quotation.id,

        "status":
        quotation.status

    }



# ==========================================
# Quotation Status Tracker
# ==========================================

@router.get("/{quotation_id}/status")
def quotation_status(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
# ==========================================
# Farmer Quotation Analytics
# ==========================================

@router.get("/farmer/analytics")
def farmer_quotation_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Shows farmer quotation performance.
    """


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can view analytics"
        )


    quotations = db.query(Quotation).filter(
        Quotation.farmer_id == current_user.id
    ).all()


    total = len(quotations)


    accepted = len([
        q for q in quotations
        if q.status == "accepted"
    ])


    rejected = len([
        q for q in quotations
        if q.status == "rejected"
    ])


    pending = len([
        q for q in quotations
        if q.status == "pending"
    ])



    return {

        "total_quotations":
        total,

        "accepted":
        accepted,

        "rejected":
        rejected,

        "pending":
        pending

    }



# ==========================================
# Customer Quotation Statistics
# ==========================================

@router.get("/customer/statistics")
def customer_quotation_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can view statistics"
        )


    quotations = db.query(Quotation).filter(
        Quotation.customer_id == current_user.id
    ).all()



    return {

        "total_received":
        len(quotations),

        "accepted":
        len([
            q for q in quotations
            if q.status == "accepted"
        ]),

        "rejected":
        len([
            q for q in quotations
            if q.status == "rejected"
        ]),

        "negotiation":
        len([
            q for q in quotations
            if q.status == "negotiation"
        ])

    }



# ==========================================
# Search Quotations
# ==========================================

@router.get("/search")
def search_quotations(
    keyword: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role == "farmer":

        quotations = db.query(Quotation).filter(
            Quotation.farmer_id == current_user.id
        ).all()


    elif current_user.role == "customer":

        quotations = db.query(Quotation).filter(
            Quotation.customer_id == current_user.id
        ).all()


    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    results = []


    for quotation in quotations:

        if (
            keyword.lower()
            in quotation.status.lower()
            or
            keyword.lower()
            in str(quotation.product_id)
        ):

            results.append({

                "quotation_id":
                quotation.id,

                "product_id":
                quotation.product_id,

                "price":
                quotation.offered_price,

                "quantity":
                quotation.quantity,

                "status":
                quotation.status

            })


    return {

        "count":
        len(results),

        "results":
        results

    }



# ==========================================
# Quotation Module Status
# ==========================================

@router.get("/")
def quotation_home():

    return {

        "module":
        "Quotation Management",

        "status":
        "active",

        "features":

        [

            "Farmer Quotations",

            "Customer Inbox",

            "Price Negotiation",

            "Accept/Reject",

            "Order Conversion",

            "Quotation Analytics"

        ]

    }