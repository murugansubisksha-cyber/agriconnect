"""
explainable_ai.py
=================

AgriConnect Explainable AI Module.

Purpose:
    - Explain AI recommendations
    - Increase farmer and buyer trust
    - Show why a match was suggested

Used with:
    - recommendation_model.py
    - scoring.py
    - quotation.py
"""


from typing import Dict, List



# ==========================================
# Explanation Categories
# ==========================================

EXPLANATION_FACTORS = [

    "product",

    "quantity",

    "location",

    "price",

    "trust"

]



# ==========================================
# Product Explanation
# ==========================================

def explain_product_match(
    score: float
):

    """
    Explains product compatibility.
    """


    if score >= 80:

        return (
            "Product requirement matches strongly."
        )


    elif score >= 50:

        return (
            "Product is partially compatible."
        )


    return (
        "Product requirement does not match well."
    )



# ==========================================
# Quantity Explanation
# ==========================================

def explain_quantity_match(
    score: float
):

    """
    Explains quantity compatibility.
    """


    if score >= 80:

        return (
            "Available quantity closely matches "
            "the required quantity."
        )


    elif score >= 50:

        return (
            "Quantity difference exists but "
            "may be manageable."
        )


    return (
        "Quantity requirement needs discussion."
    )



# ==========================================
# Location Explanation
# ==========================================

def explain_location_match(
    score: float
):

    """
    Explains location suitability.
    """


    if score >= 80:

        return (
            "Location is convenient for delivery."
        )


    elif score >= 50:

        return (
            "Location is acceptable but transport "
            "should be discussed."
        )


    return (
        "Location may increase logistics effort."
    )
# ==========================================
# Price Explanation
# ==========================================

def explain_price_match(
    score: float
):

    """
    Explains price compatibility.
    """


    if score >= 80:

        return (
            "Price expectations between farmer "
            "and buyer are close."
        )


    elif score >= 50:

        return (
            "Price difference exists. "
            "Negotiation may be required."
        )


    return (
        "Price gap is high. "
        "Both parties should discuss terms."
    )



# ==========================================
# Trust Explanation
# ==========================================

def explain_trust_score(
    score: float
):

    """
    Explains reliability score.
    """


    if score >= 85:

        return (
            "Both users have strong marketplace "
            "reliability."
        )


    elif score >= 60:

        return (
            "Users have acceptable transaction "
            "history."
        )


    return (
        "More verification is recommended."
    )



# ==========================================
# Confidence Explanation
# ==========================================

def explain_confidence(
    score: float
):

    """
    Explains transaction confidence.
    """


    if score >= 85:

        return {

            "level":
            "High",

            "message":
            "This connection looks suitable "
            "for proceeding."

        }



    elif score >= 60:

        return {

            "level":
            "Medium",

            "message":
            "Review price and agreement "
            "details before proceeding."

        }



    else:

        return {

            "level":
            "Low",

            "message":
            "More information is needed "
            "before making a decision."

        }



# ==========================================
# Factor Based Explanation
# ==========================================

def analyze_score_factors(
    breakdown: Dict
):

    """
    Converts score breakdown into
    explanations.
    """


    explanations = []



    if "product" in breakdown:

        explanations.append(

            explain_product_match(

                breakdown["product"]

            )

        )



    if "quantity" in breakdown:

        explanations.append(

            explain_quantity_match(

                breakdown["quantity"]

            )

        )



    if "location" in breakdown:

        explanations.append(

            explain_location_match(

                breakdown["location"]

            )

        )



    if "price" in breakdown:

        explanations.append(

            explain_price_match(

                breakdown["price"]

            )

        )



    if "trust" in breakdown:

        explanations.append(

            explain_trust_score(

                breakdown["trust"]

            )

        )



    return explanations
# ==========================================
# Complete Recommendation Explanation
# ==========================================

def generate_match_explanation(
    evaluation: Dict
):

    """
    Creates complete explanation
    for a recommended match.
    """


    breakdown = evaluation.get(
        "breakdown",
        {}
    )



    score = evaluation.get(
        "match_score",
        0
    )



    explanations = analyze_score_factors(

        breakdown

    )



    return {

        "match_score":
        score,

        "summary":
        generate_summary(score),

        "reasons":
        explanations

    }



# ==========================================
# Match Summary Generator
# ==========================================

def generate_summary(
    score: float
):

    """
    Generates simple match summary.
    """


    if score >= 85:

        return (
            "Highly recommended connection. "
            "This farmer and buyer have strong "
            "compatibility."
        )



    elif score >= 70:

        return (
            "Good potential connection. "
            "Some details should be confirmed."
        )



    elif score >= 50:

        return (
            "Possible connection, but "
            "discussion is needed."
        )



    return (
        "Low compatibility match."
    )



# ==========================================
# Explain Recommended Farmer
# ==========================================

def explain_farmer_recommendation(
    farmer: Dict,
    buyer: Dict,
    score_result: Dict
):

    """
    Explains why a farmer is recommended
    to a buyer.
    """


    explanation = generate_match_explanation(

        score_result

    )



    return {

        "recommended_farmer":

        {

            "id":
            farmer.get("id"),

            "name":
            farmer.get("name")

        },


        "for_buyer":

        buyer.get(
            "name"
        ),


        "why_recommended":

        explanation

    }



# ==========================================
# Explain Recommended Buyer
# ==========================================

def explain_buyer_recommendation(
    buyer: Dict,
    farmer: Dict,
    score_result: Dict
):

    """
    Explains why a buyer is recommended
    to a farmer.
    """


    explanation = generate_match_explanation(

        score_result

    )



    return {

        "recommended_buyer":

        {

            "id":
            buyer.get("id"),

            "name":
            buyer.get("name")

        },


        "for_farmer":

        farmer.get(
            "name"
        ),


        "why_recommended":

        explanation

    }



# ==========================================
# Compare Two Recommendations
# ==========================================

def compare_recommendations(
    first: Dict,
    second: Dict
):

    """
    Explains why one recommendation
    ranks higher.
    """


    first_score = first.get(
        "match_score",
        0
    )


    second_score = second.get(
        "match_score",
        0
    )



    if first_score > second_score:

        return {

            "better_option":
            first,

            "reason":
            "Higher compatibility score."

        }



    elif second_score > first_score:

        return {

            "better_option":
            second,

            "reason":
            "Higher compatibility score."

        }



    return {

        "better_option":
        None,

        "reason":
        "Both options have similar scores."

    }
# ==========================================
# Natural Language Explanation Generator
# ==========================================

def generate_natural_explanation(
    match_data: Dict
):

    """
    Converts AI scores into a simple
    marketplace explanation.
    """


    score = match_data.get(
        "match_score",
        0
    )


    reasons = match_data.get(
        "reasons",
        []
    )



    explanation = {

        "overall":

        generate_summary(
            score
        ),

        "details":

        reasons

    }



    return explanation



# ==========================================
# Farmer Friendly Explanation
# ==========================================

def farmer_explanation(
    farmer_name: str,
    buyer_name: str,
    score: float
):

    """
    Explanation written for farmers.
    """


    if score >= 80:

        message = (

            f"{buyer_name} is a good buyer "
            f"match for {farmer_name}. "
            "The product requirement, "
            "price expectation and transaction "
            "history are suitable."

        )


    elif score >= 50:

        message = (

            f"{buyer_name} may be suitable, "
            "but confirm price and delivery "
            "details before accepting."

        )


    else:

        message = (

            f"{buyer_name} has a lower match "
            "score. Review details carefully."

        )



    return message



# ==========================================
# Buyer Friendly Explanation
# ==========================================

def buyer_explanation(
    buyer_name: str,
    farmer_name: str,
    score: float
):

    """
    Explanation written for buyers.
    """


    if score >= 80:

        message = (

            f"{farmer_name} is strongly "
            f"recommended for {buyer_name} "
            "because requirements match well."

        )


    elif score >= 50:

        message = (

            f"{farmer_name} can be considered. "
            "Discuss remaining details."

        )


    else:

        message = (

            f"{farmer_name} has limited "
            "compatibility for this requirement."

        )



    return message



# ==========================================
# Tamil Explanation Support
# ==========================================

def translate_explanation_to_tamil(
    explanation: str
):

    """
    Tamil language explanation layer.

    Future:
        - Indic NLP model
        - Translation API
        - Tamil LLM
    """


    return {

        "language":
        "tamil",

        "text":
        explanation

    }



# ==========================================
# User Feedback Storage
# ==========================================

explanation_feedback = []



def save_explanation_feedback(
    user_id: int,
    recommendation_id: int,
    feedback: str
):

    """
    Stores user feedback.

    Future:
        Use feedback to improve AI.
    """


    explanation_feedback.append({

        "user_id":
        user_id,

        "recommendation_id":
        recommendation_id,

        "feedback":
        feedback

    })


    return True
# ==========================================
# Complete Explainable AI Pipeline
# ==========================================

def explain_recommendation(
    user_type: str,
    user: Dict,
    recommended_user: Dict,
    match_result: Dict
):

    """
    Complete explanation generator.

    user_type:
        farmer
        buyer
    """


    explanation = generate_match_explanation(

        match_result

    )



    score = match_result.get(

        "match_score",

        0

    )



    if user_type == "farmer":


        user_message = farmer_explanation(

            user.get(
                "name",
                "Farmer"
            ),

            recommended_user.get(
                "name",
                "Buyer"
            ),

            score

        )



    else:


        user_message = buyer_explanation(

            user.get(
                "name",
                "Buyer"
            ),

            recommended_user.get(
                "name",
                "Farmer"
            ),

            score

        )



    return {

        "score":
        score,

        "summary":
        explanation.get(
            "summary"
        ),

        "reasons":
        explanation.get(
            "reasons"
        ),

        "simple_explanation":
        user_message

    }



# ==========================================
# Explanation API Response Formatter
# ==========================================

def format_explanation_response(
    explanation: Dict
):

    """
    Formats output for FastAPI routes.
    """


    return {

        "match_score":
        explanation.get(
            "score"
        ),

        "why_recommended":
        explanation.get(
            "simple_explanation"
        ),

        "technical_details":

        {

            "summary":
            explanation.get(
                "summary"
            ),

            "factors":
            explanation.get(
                "reasons"
            )

        }

    }



# ==========================================
# AI Decision Transparency Report
# ==========================================

def generate_transparency_report(
    recommendation_id: int,
    explanation: Dict
):

    """
    Creates a report showing how
    AI reached the decision.
    """


    return {

        "recommendation_id":
        recommendation_id,

        "decision_score":
        explanation.get(
            "score"
        ),

        "decision_factors":
        explanation.get(
            "reasons"
        ),

        "human_explanation":
        explanation.get(
            "simple_explanation"
        )

    }



# ==========================================
# Learning From Feedback
# ==========================================

def analyze_feedback():

    """
    Future improvement system.

    Uses user feedback to improve:
        - scoring weights
        - recommendation quality
        - explanation quality
    """


    total_feedback = len(
        explanation_feedback
    )


    return {

        "feedback_count":
        total_feedback,

        "status":
        "Learning data collected"

    }



# ==========================================
# Explainable AI Module Status
# ==========================================

def explainable_ai_status():

    return {

        "module":
        "AgriConnect Explainable AI",

        "status":
        "active",

        "purpose":
        "Explain why farmer-buyer matches are recommended",

        "features":

        [

            "Match Explanation",

            "Score Breakdown",

            "Farmer Friendly Messages",

            "Buyer Friendly Messages",

            "Tamil Explanation Support",

            "Decision Transparency",

            "Feedback Learning"

        ]

    }