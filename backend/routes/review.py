"""
review.py
=========

Review and rating management routes for AgriConnect.

Features:
    - Customer product reviews
    - Farmer ratings
    - Review management
    - Trust score calculation
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Review,
    Product,
    Order
)

from backend.schemas import (
    ReviewCreate,
    ReviewUpdate
)

from backend.auth import get_current_user



router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)



# ==========================================
# Create Review
# ==========================================

@router.post("/")
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer reviews purchased product.
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can create reviews"
        )


    product = db.query(Product).filter(
        Product.id == review_data.product_id
    ).first()


    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    # Check purchase history

    order = db.query(Order).filter(
        Order.customer_id == current_user.id,
        Order.product_id == review_data.product_id,
        Order.status == "delivered"
    ).first()


    if not order:

        raise HTTPException(
            status_code=400,
            detail="You can review only purchased products"
        )



    existing_review = db.query(Review).filter(
        Review.customer_id == current_user.id,
        Review.product_id == review_data.product_id
    ).first()



    if existing_review:

        raise HTTPException(
            status_code=400,
            detail="You already reviewed this product"
        )



    review = Review(

        customer_id=current_user.id,

        product_id=review_data.product_id,

        farmer_id=product.farmer_id,

        rating=review_data.rating,

        comment=review_data.comment

    )



    db.add(review)

    db.commit()

    db.refresh(review)



    return {

        "message":
        "Review added successfully",

        "review_id":
        review.id

    }
# ==========================================
# View Product Reviews
# ==========================================

@router.get("/product/{product_id}")
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):

    """
    Shows all reviews for a product.
    """


    product = db.query(Product).filter(
        Product.id == product_id
    ).first()


    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )



    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(
        Review.created_at.desc()
    ).all()



    result = []


    for review in reviews:

        result.append({

            "review_id":
            review.id,

            "customer_id":
            review.customer_id,

            "rating":
            review.rating,

            "comment":
            review.comment,

            "date":
            review.created_at

        })



    return {

        "product_id":
        product_id,

        "total_reviews":
        len(result),

        "reviews":
        result

    }



# ==========================================
# View Farmer Reviews
# ==========================================

@router.get("/farmer/{farmer_id}")
def get_farmer_reviews(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    """
    Shows farmer reputation based on reviews.
    """


    reviews = db.query(Review).filter(
        Review.farmer_id == farmer_id
    ).order_by(
        Review.created_at.desc()
    ).all()



    if not reviews:

        return {

            "farmer_id":
            farmer_id,

            "average_rating":
            0,

            "total_reviews":
            0,

            "reviews":
            []

        }



    total_rating = sum(
        review.rating
        for review in reviews
    )


    average_rating = (
        total_rating / len(reviews)
    )



    result = []


    for review in reviews:

        result.append({

            "review_id":
            review.id,

            "product_id":
            review.product_id,

            "rating":
            review.rating,

            "comment":
            review.comment,

            "date":
            review.created_at

        })



    return {

        "farmer_id":
        farmer_id,

        "average_rating":
        round(average_rating, 2),

        "total_reviews":
        len(result),

        "reviews":
        result

    }



# ==========================================
# Customer Review History
# ==========================================

@router.get("/customer/history")
def customer_review_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can view review history"
        )



    reviews = db.query(Review).filter(
        Review.customer_id == current_user.id
    ).order_by(
        Review.created_at.desc()
    ).all()



    history = []


    for review in reviews:

        history.append({

            "review_id":
            review.id,

            "product_id":
            review.product_id,

            "rating":
            review.rating,

            "comment":
            review.comment,

            "date":
            review.created_at

        })



    return {

        "total_reviews":
        len(history),

        "reviews":
        history

    }



# ==========================================
# View Single Review
# ==========================================

@router.get("/{review_id}")
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):


    review = db.query(Review).filter(
        Review.id == review_id
    ).first()



    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )



    return {

        "review_id":
        review.id,

        "customer_id":
        review.customer_id,

        "product_id":
        review.product_id,

        "farmer_id":
        review.farmer_id,

        "rating":
        review.rating,

        "comment":
        review.comment,

        "created_at":
        review.created_at

    }
# ==========================================
# Update Review
# ==========================================

@router.put("/{review_id}")
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer updates their review.
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can update reviews"
        )


    review = db.query(Review).filter(
        Review.id == review_id
    ).first()


    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )


    if review.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot edit this review"
        )



    if review_data.rating:

        if review_data.rating < 1 or review_data.rating > 5:

            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1 and 5"
            )


        review.rating = review_data.rating



    if review_data.comment:

        review.comment = review_data.comment



    db.commit()

    db.refresh(review)



    return {

        "message":
        "Review updated successfully",

        "review_id":
        review.id

    }



# ==========================================
# Delete Review
# ==========================================

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Customer deletes own review.
    """


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can delete reviews"
        )



    review = db.query(Review).filter(
        Review.id == review_id
    ).first()



    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )



    if review.customer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot delete this review"
        )



    db.delete(review)

    db.commit()



    return {

        "message":
        "Review deleted successfully"

    }



# ==========================================
# Validate Rating
# ==========================================

def validate_rating(rating):

    """
    Internal helper function
    """

    if rating < 1 or rating > 5:

        raise HTTPException(
            status_code=400,
            detail="Rating should be between 1 and 5"
        )



# ==========================================
# Farmer Respond To Review
# ==========================================

@router.put("/{review_id}/response")
def farmer_response(
    review_id: int,
    response: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Farmer replies to customer feedback.
    """


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can respond"
        )



    review = db.query(Review).filter(
        Review.id == review_id
    ).first()



    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )



    if review.farmer_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="This review is not for you"
        )



    review.farmer_response = response


    db.commit()

    db.refresh(review)



    return {

        "message":
        "Response added successfully",

        "review_id":
        review.id,

        "response":
        review.farmer_response

    }
# ==========================================
# Review Analytics
# ==========================================

@router.get("/analytics/summary")
def review_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Review statistics for users.
    """


    if current_user.role == "farmer":

        reviews = db.query(Review).filter(
            Review.farmer_id == current_user.id
        ).all()


    elif current_user.role == "customer":

        reviews = db.query(Review).filter(
            Review.customer_id == current_user.id
        ).all()


    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    total_reviews = len(reviews)



    if total_reviews == 0:

        return {

            "total_reviews": 0,

            "average_rating": 0,

            "rating_distribution": {}

        }



    average_rating = sum(
        review.rating
        for review in reviews
    ) / total_reviews



    distribution = {

        "5_star": 0,

        "4_star": 0,

        "3_star": 0,

        "2_star": 0,

        "1_star": 0

    }



    for review in reviews:

        if review.rating == 5:

            distribution["5_star"] += 1

        elif review.rating == 4:

            distribution["4_star"] += 1

        elif review.rating == 3:

            distribution["3_star"] += 1

        elif review.rating == 2:

            distribution["2_star"] += 1

        elif review.rating == 1:

            distribution["1_star"] += 1



    return {

        "total_reviews":
        total_reviews,

        "average_rating":
        round(average_rating, 2),

        "rating_distribution":
        distribution

    }



# ==========================================
# Farmer Trust Score
# ==========================================

@router.get("/farmer/{farmer_id}/trust-score")
def farmer_trust_score(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    """
    Calculates farmer reliability score.

    Used for:
        - Buyer confidence
        - Recommendation ranking
    """


    reviews = db.query(Review).filter(
        Review.farmer_id == farmer_id
    ).all()



    if not reviews:

        return {

            "farmer_id":
            farmer_id,

            "trust_score":
            0

        }



    average_rating = sum(
        review.rating
        for review in reviews
    ) / len(reviews)



    # Simple trust score formula
    trust_score = (
        average_rating / 5
    ) * 100



    return {

        "farmer_id":
        farmer_id,

        "total_reviews":
        len(reviews),

        "average_rating":
        round(average_rating, 2),

        "trust_score":
        round(trust_score, 2)

    }



# ==========================================
# Top Rated Products
# ==========================================

@router.get("/top-products")
def top_rated_products(
    db: Session = Depends(get_db)
):
# ==========================================

@router.get("/analytics/summary")
def review_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Review statistics for users.
    """


    if current_user.role == "farmer":

        reviews = db.query(Review).filter(
            Review.farmer_id == current_user.id
        ).all()


    elif current_user.role == "customer":

        reviews = db.query(Review).filter(
            Review.customer_id == current_user.id
        ).all()


    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    total_reviews = len(reviews)



    if total_reviews == 0:

        return {

            "total_reviews": 0,

            "average_rating": 0,

            "rating_distribution": {}

        }



    average_rating = sum(
        review.rating
        for review in reviews
    ) / total_reviews



    distribution = {

        "5_star": 0,

        "4_star": 0,

        "3_star": 0,

        "2_star": 0,

        "1_star": 0

    }



    for review in reviews:

        if review.rating == 5:

            distribution["5_star"] += 1

        elif review.rating == 4:

            distribution["4_star"] += 1

        elif review.rating == 3:

            distribution["3_star"] += 1

        elif review.rating == 2:

            distribution["2_star"] += 1

        elif review.rating == 1:

            distribution["1_star"] += 1



    return {

        "total_reviews":
        total_reviews,

        "average_rating":
        round(average_rating, 2),

        "rating_distribution":
        distribution

    }



# ==========================================
# Farmer Trust Score
# ==========================================

@router.get("/farmer/{farmer_id}/trust-score")
def farmer_trust_score(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    """
    Calculates farmer reliability score.

    Used for:
        - Buyer confidence
        - Recommendation ranking
    """


    reviews = db.query(Review).filter(
        Review.farmer_id == farmer_id
    ).all()



    if not reviews:

        return {

            "farmer_id":
            farmer_id,

            "trust_score":
            0

        }



    average_rating = sum(
        review.rating
        for review in reviews
    ) / len(reviews)



    # Simple trust score formula
    trust_score = (
        average_rating / 5
    ) * 100



    return {

        "farmer_id":
        farmer_id,

        "total_reviews":
        len(reviews),

        "average_rating":
        round(average_rating, 2),

        "trust_score":
        round(trust_score, 2)

    }



# ==========================================
# Top Rated Products
# ==========================================

@router.get("/top-products")
def top_rated_products(
    db: Session = Depends(get_db)
):

    """
    Returns products with best ratings.
    """


    products = db.query(Product).all()



    ranking = []



    for product in products:


        reviews = db.query(Review).filter(
            Review.product_id == product.id
        ).all()



        if reviews:


            average = sum(
                review.rating
                for review in reviews
            ) / len(reviews)



            ranking.append({

                "product_id":
                product.id,

                "average_rating":
                round(average, 2),

                "total_reviews":
                len(reviews)

            })



    ranking.sort(
        key=lambda x: x["average_rating"],
        reverse=True
    )



    return {

        "top_products":
        ranking[:10]

    }
# ==========================================
# Search Reviews
# ==========================================

@router.get("/search")
def search_reviews(
    keyword: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    """
    Search reviews by comment,
    product id, or rating.
    """


    if current_user.role == "farmer":

        reviews = db.query(Review).filter(
            Review.farmer_id == current_user.id
        ).all()


    elif current_user.role == "customer":

        reviews = db.query(Review).filter(
            Review.customer_id == current_user.id
        ).all()


    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )



    results = []


    for review in reviews:

        if (
            keyword.lower()
            in review.comment.lower()

            or

            keyword
            in str(review.rating)

            or

            keyword
            in str(review.product_id)
        ):

            results.append({

                "review_id":
                review.id,

                "product_id":
                review.product_id,

                "rating":
                review.rating,

                "comment":
                review.comment

            })



    return {

        "count":
        len(results),

        "reviews":
        results

    }



# ==========================================
# Filter Reviews By Rating
# ==========================================

@router.get("/filter")
def filter_reviews(
    rating: int = None,
    db: Session = Depends(get_db)
):

    """
    Filter reviews based on star rating.
    """


    query = db.query(Review)



    if rating:

        if rating < 1 or rating > 5:

            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1 and 5"
            )


        query = query.filter(
            Review.rating == rating
        )



    reviews = query.all()



    result = []


    for review in reviews:

        result.append({

            "review_id":
            review.id,

            "product_id":
            review.product_id,

            "rating":
            review.rating,

            "comment":
            review.comment

        })



    return {

        "total":
        len(result),

        "reviews":
        result

    }



# ==========================================
# Farmer Review Dashboard
# ==========================================

@router.get("/farmer/dashboard")
def farmer_review_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can access dashboard"
        )



    reviews = db.query(Review).filter(
        Review.farmer_id == current_user.id
    ).all()



    total_reviews = len(reviews)



    average_rating = 0


    if total_reviews > 0:

        average_rating = (
            sum(
                review.rating
                for review in reviews
            )
            /
            total_reviews
        )



    responses = len([
        review
        for review in reviews
        if review.farmer_response
    ])



    return {

        "farmer_id":
        current_user.id,

        "total_reviews":
        total_reviews,

        "average_rating":
        round(average_rating, 2),

        "responses_given":
        responses

    }



# ==========================================
# Customer Feedback Summary
# ==========================================

@router.get("/customer/summary")
def customer_feedback_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):


    if current_user.role != "customer":

        raise HTTPException(
            status_code=403,
            detail="Only customers can view summary"
        )



    reviews = db.query(Review).filter(
        Review.customer_id == current_user.id
    ).all()



    return {

        "customer_id":
        current_user.id,

        "total_reviews":
        len(reviews),

        "products_reviewed":
        len(
            set(
                review.product_id
                for review in reviews
            )
        )

    }



# ==========================================
# Review Module Status
# ==========================================

@router.get("/")
def review_home():

    return {

        "module":
        "Review Management",

        "status":
        "active",

        "features":

        [

            "Product Reviews",

            "Farmer Ratings",

            "Trust Score",

            "Review Analytics",

            "Feedback System",

            "Rating Distribution"

        ]

    }