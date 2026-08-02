"""
scoring.py
==========

AgriConnect AI Scoring Engine.

Purpose:
    - Calculate marketplace match scores
    - Evaluate farmer-buyer compatibility
    - Rank transaction quality

Used by:
    - recommendation_model.py
    - quotation.py
    - chatbot.py
"""


from typing import Dict, List



# ==========================================
# Scoring Weights
# ==========================================

SCORING_WEIGHTS = {

    "product": 0.30,

    "quantity": 0.20,

    "location": 0.15,

    "price": 0.15,

    "trust": 0.20

}



# ==========================================
# Product Compatibility Score
# ==========================================

def product_score(
    farmer_product: str,
    buyer_product: str
):

    """
    Checks product compatibility.
    """


    if not farmer_product or not buyer_product:

        return 0



    if (
        farmer_product.lower()
        ==
        buyer_product.lower()
    ):

        return 100



    return 50



# ==========================================
# Quantity Compatibility Score
# ==========================================

def quantity_score(
    available_quantity: float,
    required_quantity: float
):

    """
    Checks quantity suitability.
    """


    if required_quantity <= 0:

        return 0



    difference = abs(
        available_quantity -
        required_quantity
    )



    score = 100 - (
        difference /
        required_quantity
        *
        100
    )


    return max(
        0,
        round(score,2)
    )



# ==========================================
# Location Score
# ==========================================

def location_score(
    farmer_location: str,
    buyer_location: str
):

    """
    Location compatibility.

    Future:
        GPS distance calculation.
    """


    if (
        farmer_location.lower()
        ==
        buyer_location.lower()
    ):

        return 100



    return 60# ==========================================
# Price Compatibility Score
# ==========================================

def price_score(
    farmer_expected_price: float,
    buyer_offered_price: float
):

    """
    Checks whether buyer and farmer
    price expectations are close.
    """


    if (
        farmer_expected_price <= 0
        or
        buyer_offered_price <= 0
    ):

        return 0



    difference = abs(
        farmer_expected_price
        -
        buyer_offered_price
    )



    percentage_difference = (

        difference
        /
        farmer_expected_price

    ) * 100



    score = 100 - percentage_difference



    return max(
        0,
        round(score, 2)
    )



# ==========================================
# Farmer Reliability Score
# ==========================================

def farmer_reliability_score(
    farmer: Dict
):

    """
    Calculates farmer reliability.

    Factors:
        - Rating
        - Completed orders
        - Response rate
        - Verification
    """


    rating = (

        farmer.get(
            "rating",
            0
        )
        /
        5

    ) * 100



    completed_orders = min(

        farmer.get(
            "completed_orders",
            0
        )
        /
        100
        *
        100,

        100

    )



    response_rate = farmer.get(

        "response_rate",

        0

    )



    verification = (

        100
        if farmer.get(
            "verified",
            False
        )

        else

        50

    )



    score = (

        rating * 0.4

        +

        completed_orders * 0.2

        +

        response_rate * 0.2

        +

        verification * 0.2

    )



    return round(
        score,
        2
    )



# ==========================================
# Buyer Reliability Score
# ==========================================

def buyer_reliability_score(
    buyer: Dict
):

    """
    Calculates buyer trust score.

    Factors:
        - Previous purchases
        - Payment history
        - Verification
        - Response behavior
    """


    purchase_history = min(

        buyer.get(
            "completed_orders",
            0
        )
        /
        100
        *
        100,

        100

    )



    payment_score = buyer.get(

        "payment_success_rate",

        0

    )



    response_score = buyer.get(

        "response_rate",

        0

    )



    verification_score = (

        100
        if buyer.get(
            "verified",
            False
        )

        else

        50

    )



    score = (

        purchase_history * 0.3

        +

        payment_score * 0.3

        +

        response_score * 0.2

        +

        verification_score * 0.2

    )



    return round(
        score,
        2
    )



# ==========================================
# General Trust Score
# ==========================================

def trust_score(
    user: Dict,
    user_type: str
):

    """
    Returns reliability score
    based on account type.
    """


    if user_type == "farmer":

        return farmer_reliability_score(
            user
        )



    elif user_type == "buyer":

        return buyer_reliability_score(
            user
        )



    return 0
# ==========================================
# Complete Marketplace Match Score
# ==========================================

def calculate_marketplace_score(
    farmer: Dict,
    buyer: Dict
):

    """
    Calculates complete farmer-buyer
    compatibility score.
    """


    product = product_score(

        farmer.get(
            "product",
            ""
        ),

        buyer.get(
            "required_product",
            ""
        )

    )



    quantity = quantity_score(

        farmer.get(
            "quantity",
            0
        ),

        buyer.get(
            "required_quantity",
            0
        )

    )



    location = location_score(

        farmer.get(
            "location",
            ""
        ),

        buyer.get(
            "location",
            ""
        )

    )



    price = price_score(

        farmer.get(
            "expected_price",
            0
        ),

        buyer.get(
            "offered_price",
            0
        )

    )



    trust = (

        farmer_reliability_score(
            farmer
        )

        +

        buyer_reliability_score(
            buyer
        )

    ) / 2



    final_score = (

        product *
        SCORING_WEIGHTS["product"]

        +

        quantity *
        SCORING_WEIGHTS["quantity"]

        +

        location *
        SCORING_WEIGHTS["location"]

        +

        price *
        SCORING_WEIGHTS["price"]

        +

        trust *
        SCORING_WEIGHTS["trust"]

    )



    return {

        "overall_score":
        round(
            final_score,
            2
        ),

        "breakdown":

        {

            "product":
            product,

            "quantity":
            quantity,

            "location":
            location,

            "price":
            price,

            "trust":
            round(
                trust,
                2
            )

        }

    }



# ==========================================
# Marketplace Ranking Score
# ==========================================

def ranking_score(
    match_result: Dict
):

    """
    Converts match result into
    ranking value.
    """


    return match_result.get(

        "overall_score",

        0

    )



# ==========================================
# Quotation Evaluation Score
# ==========================================

def quotation_score(
    quotation: Dict
):

    """
    Evaluates quotation quality.

    Checks:
        - Price
        - Payment clarity
        - Delivery clarity
        - Buyer verification
    """


    score = 0



    if quotation.get(
        "price"
    ):

        score += 25



    if quotation.get(
        "payment_terms"
    ):

        score += 25



    if quotation.get(
        "delivery_details"
    ):

        score += 25



    if quotation.get(
        "buyer_verified"
    ):

        score += 25



    return score



# ==========================================
# Transaction Confidence Score
# ==========================================

def transaction_confidence(
    farmer: Dict,
    buyer: Dict,
    quotation: Dict
):

    """
    Predicts confidence level
    before transaction.
    """


    marketplace = calculate_marketplace_score(

        farmer,

        buyer

    )



    quotation_value = quotation_score(

        quotation

    )



    confidence = (

        marketplace["overall_score"]
        *
        0.7

        +

        quotation_value
        *
        0.3

    )



    return {

        "confidence_score":
        round(
            confidence,
            2
        ),

        "recommendation":

        (

            "Safe to proceed"

            if confidence >= 75

            else

            "Review details before proceeding"

        )

    }
# ==========================================
# Score Multiple Farmers For Buyer
# ==========================================

def score_farmers_for_buyer(
    buyer: Dict,
    farmers: List[Dict]
):

    """
    Scores all farmers for a buyer.
    """


    results = []



    for farmer in farmers:


        score = calculate_marketplace_score(

            farmer,

            buyer

        )



        results.append({

            "farmer_id":
            farmer.get("id"),

            "farmer_name":
            farmer.get("name"),

            "score":
            score["overall_score"],

            "details":
            score["breakdown"]

        })



    results.sort(

        key=lambda x:
        x["score"],

        reverse=True

    )



    return results



# ==========================================
# Score Multiple Buyers For Farmer
# ==========================================

def score_buyers_for_farmer(
    farmer: Dict,
    buyers: List[Dict]
):

    """
    Scores all buyers for a farmer.
    """


    results = []



    for buyer in buyers:


        score = calculate_marketplace_score(

            farmer,

            buyer

        )



        results.append({

            "buyer_id":
            buyer.get("id"),

            "buyer_name":
            buyer.get("name"),

            "score":
            score["overall_score"],

            "details":
            score["breakdown"]

        })



    results.sort(

        key=lambda x:
        x["score"],

        reverse=True

    )



    return results



# ==========================================
# Generate Score Explanation
# ==========================================

def explain_score(
    score_details: Dict
):

    """
    Converts score into human-readable
    explanation.
    """


    explanation = []



    if score_details.get(
        "product",
        0
    ) >= 80:

        explanation.append(
            "Product requirement matches well."
        )



    if score_details.get(
        "quantity",
        0
    ) >= 80:

        explanation.append(
            "Quantity requirement is suitable."
        )



    if score_details.get(
        "location",
        0
    ) >= 80:

        explanation.append(
            "Location is convenient."
        )



    if score_details.get(
        "price",
        0
    ) >= 80:

        explanation.append(
            "Price expectations are close."
        )



    if score_details.get(
        "trust",
        0
    ) >= 80:

        explanation.append(
            "Both users have good reliability."
        )



    if not explanation:

        explanation.append(
            "More details should be verified."
        )



    return explanation



# ==========================================
# Prepare Database Record
# ==========================================

def create_scoring_record(
    farmer_id: int,
    buyer_id: int,
    score_result: Dict
):

    """
    Creates database-ready scoring data.

    Future:
        Save into MatchScore table.
    """


    return {

        "farmer_id":
        farmer_id,

        "buyer_id":
        buyer_id,

        "score":
        score_result.get(
            "overall_score"
        ),

        "details":
        score_result.get(
            "breakdown"
        )

    }



# ==========================================
# Match Quality Category
# ==========================================

def score_category(
    score: float
):


    if score >= 85:

        return "Excellent Match"



    elif score >= 70:

        return "Good Match"



    elif score >= 50:

        return "Average Match"



    else:

        return "Low Match"
# ==========================================
# Complete Match Evaluation Pipeline
# ==========================================

def evaluate_marketplace_match(
    farmer: Dict,
    buyer: Dict
):

    """
    Complete farmer-buyer evaluation.

    Returns:
        - Match score
        - Category
        - Explanation
        - Trust information
    """


    result = calculate_marketplace_score(

        farmer,

        buyer

    )



    score = result.get(
        "overall_score",
        0
    )



    return {

        "farmer_id":
        farmer.get("id"),

        "buyer_id":
        buyer.get("id"),

        "match_score":
        score,

        "category":
        score_category(
            score
        ),

        "explanation":
        explain_score(
            result["breakdown"]
        ),

        "breakdown":
        result["breakdown"]

    }



# ==========================================
# Compare Multiple Matches
# ==========================================

def compare_matches(
    matches: List[Dict]
):

    """
    Sorts multiple match results.
    """


    matches.sort(

        key=lambda x:
        x.get(
            "match_score",
            0
        ),

        reverse=True

    )



    return matches



# ==========================================
# Generate Buyer Suggestions
# ==========================================

def generate_buyer_suggestions(
    farmer: Dict,
    buyers: List[Dict]
):

    """
    Returns best buyers for farmer.
    """


    results = []



    for buyer in buyers:


        evaluation = evaluate_marketplace_match(

            farmer,

            buyer

        )


        results.append(
            evaluation
        )



    return compare_matches(
        results
    )



# ==========================================
# Generate Farmer Suggestions
# ==========================================

def generate_farmer_suggestions(
    buyer: Dict,
    farmers: List[Dict]
):

    """
    Returns best farmers for buyer.
    """


    results = []



    for farmer in farmers:


        evaluation = evaluate_marketplace_match(

            farmer,

            buyer

        )


        results.append(
            evaluation
        )



    return compare_matches(
        results
    )



# ==========================================
# Route Response Formatter
# ==========================================

def format_match_response(
    evaluation: Dict
):

    """
    Formats AI result for API response.
    """


    return {

        "match_score":
        evaluation.get(
            "match_score"
        ),

        "match_type":
        evaluation.get(
            "category"
        ),

        "why_recommended":
        evaluation.get(
            "explanation"
        ),

        "score_details":
        evaluation.get(
            "breakdown"
        )

    }



# ==========================================
# Scoring Module Information
# ==========================================

def scoring_module_status():

    return {

        "module":
        "AgriConnect AI Scoring Engine",

        "status":
        "active",

        "purpose":
        "Evaluate farmer-buyer marketplace compatibility",

        "features":

        [

            "Product Compatibility",

            "Quantity Matching",

            "Location Matching",

            "Price Evaluation",

            "Trust Scoring",

            "Quotation Evaluation",

            "Transaction Confidence",

            "Match Ranking"

        ]

    }