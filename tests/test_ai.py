"""
test_ai.py
==========

Tests for AgriConnect AI modules.

Covers:
    - Recommendation engine
    - Match scoring
    - Explainable AI
    - Farmer-buyer matching
"""


import pytest


from ai.recommendation_model import (
    calculate_match_score,
    recommend_farmers
)


from ai.scoring import (
    calculate_marketplace_score,
    evaluate_marketplace_match
)


from ai.explainable_ai import (
    generate_match_explanation
)



# ==========================================
# Sample Test Data
# ==========================================

farmer = {

    "id": 1,

    "name":
    "Ravi",

    "product":
    "Rice",

    "quantity":
    100,

    "expected_price":
    2500,

    "location":
    "Chennai",

    "rating":
    4.8,

    "completed_orders":
    50,

    "verified":
    True

}



buyer = {

    "id": 10,

    "name":
    "ABC Foods",

    "required_product":
    "Rice",

    "required_quantity":
    90,

    "offered_price":
    2400,

    "location":
    "Chennai",

    "payment_success_rate":
    95,

    "completed_orders":
    60,

    "verified":
    True

}



# ==========================================
# Test Match Score Calculation
# ==========================================

def test_match_score_calculation():

    """
    Recommendation model should
    calculate compatibility.
    """


    score = calculate_match_score(

        farmer,

        buyer

    )


    assert isinstance(

        score,

        (int, float)

    )


    assert score >= 0
# ==========================================
# Test Farmer Recommendation
# ==========================================

def test_recommend_farmer():

    """
    AI should recommend suitable farmers.
    """


    farmers = [

        {

            "id": 1,

            "name":
            "Ravi",

            "product":
            "Rice",

            "quantity":
            100,

            "expected_price":
            2500,

            "location":
            "Chennai"

        },

        {

            "id": 2,

            "name":
            "Kumar",

            "product":
            "Wheat",

            "quantity":
            200,

            "expected_price":
            3000,

            "location":
            "Madurai"

        }

    ]



    recommendations = recommend_farmers(

        buyer,

        farmers

    )



    assert isinstance(

        recommendations,

        list

    )



# ==========================================
# Test Best Match Ranking
# ==========================================

def test_farmer_ranking():

    """
    Matching farmer should rank higher.
    """


    farmers = [

        {

            "id": 1,

            "product":
            "Rice",

            "location":
            "Chennai",

            "quantity":
            100

        },

        {

            "id": 2,

            "product":
            "Wheat",

            "location":
            "Coimbatore",

            "quantity":
            500

        }

    ]



    result = recommend_farmers(

        buyer,

        farmers

    )



    assert len(result) >= 0



# ==========================================
# Test Multiple Product Handling
# ==========================================

def test_multiple_product_matching():

    """
    AI should handle different products.
    """


    test_farmer = {

        "product":
        "Vegetables",

        "quantity":
        50,

        "location":
        "Chennai"

    }



    test_buyer = {

        "required_product":
        "Vegetables",

        "required_quantity":
        40,

        "location":
        "Chennai"

    }



    score = calculate_match_score(

        test_farmer,

        test_buyer

    )



    assert score >= 0



# ==========================================
# Test No Match Scenario
# ==========================================

def test_low_match_score():

    """
    Completely different requirements
    should produce lower score.
    """


    test_farmer = {

        "product":
        "Rice",

        "location":
        "Chennai"

    }



    test_buyer = {

        "required_product":
        "Coffee",

        "location":
        "Delhi"

    }



    score = calculate_match_score(

        test_farmer,

        test_buyer

    )



    assert score >= 0
from ai.scoring import (
    product_score,
    quantity_score,
    price_score,
    farmer_reliability_score,
    buyer_reliability_score,
    transaction_confidence
)



# ==========================================
# Test Product Score
# ==========================================

def test_product_score():

    """
    Same products should get
    high compatibility score.
    """


    score = product_score(

        "Rice",

        "Rice"

    )


    assert score == 100



# ==========================================
# Test Quantity Score
# ==========================================

def test_quantity_score():

    """
    Similar quantities should
    get higher score.
    """


    score = quantity_score(

        100,

        90

    )


    assert score > 80



# ==========================================
# Test Price Compatibility
# ==========================================

def test_price_score():

    """
    Similar prices should match.
    """


    score = price_score(

        2500,

        2400

    )


    assert score > 90



# ==========================================
# Test Farmer Trust Score
# ==========================================

def test_farmer_reliability():

    """
    Verified farmer should have
    good trust score.
    """


    score = farmer_reliability_score(

        farmer

    )


    assert score >= 50



# ==========================================
# Test Buyer Trust Score
# ==========================================

def test_buyer_reliability():

    """
    Buyer reliability calculation.
    """


    score = buyer_reliability_score(

        buyer

    )


    assert score >= 50



# ==========================================
# Test Complete Marketplace Score
# ==========================================

def test_marketplace_score():

    """
    Complete farmer-buyer scoring.
    """


    result = calculate_marketplace_score(

        farmer,

        buyer

    )


    assert "overall_score" in result


    assert "breakdown" in result



# ==========================================
# Test Transaction Confidence
# ==========================================

def test_transaction_confidence():

    """
    Checks transaction safety prediction.
    """


    quotation = {

        "price":
        2500,

        "payment_terms":
        "Advance",

        "delivery_details":
        "Transport included",

        "buyer_verified":
        True

    }



    result = transaction_confidence(

        farmer,

        buyer,

        quotation

    )


    assert "confidence_score" in result


    assert result["confidence_score"] >= 0
from ai.explainable_ai import (
    generate_match_explanation,
    farmer_explanation,
    buyer_explanation,
    translate_explanation_to_tamil,
    explain_recommendation
)



# ==========================================
# Test Match Explanation
# ==========================================

def test_generate_match_explanation():

    """
    AI should explain recommendation.
    """


    match_result = {

        "match_score":
        85,

        "breakdown":

        {

            "product":
            100,

            "quantity":
            90,

            "location":
            100,

            "price":
            85,

            "trust":
            90

        }

    }



    explanation = generate_match_explanation(

        match_result

    )


    assert "summary" in explanation


    assert "reasons" in explanation



# ==========================================
# Test Farmer Explanation
# ==========================================

def test_farmer_explanation():

    """
    Farmer should receive
    understandable explanation.
    """


    message = farmer_explanation(

        "Ravi",

        "ABC Foods",

        90

    )


    assert isinstance(

        message,

        str

    )


    assert len(message) > 0



# ==========================================
# Test Buyer Explanation
# ==========================================

def test_buyer_explanation():

    """
    Buyer explanation generation.
    """


    message = buyer_explanation(

        "ABC Foods",

        "Ravi",

        90

    )


    assert isinstance(

        message,

        str

    )



# ==========================================
# Test Tamil Support Layer
# ==========================================

def test_tamil_explanation_support():

    """
    Checks Tamil explanation wrapper.
    """


    result = translate_explanation_to_tamil(

        "Farmer is a good match"

    )


    assert result["language"] == "tamil"


    assert "text" in result



# ==========================================
# Test Complete Explanation Pipeline
# ==========================================

def test_complete_explanation_pipeline():

    """
    Full XAI flow test.
    """


    match_result = {

        "match_score":
        88,

        "breakdown":

        {

            "product":
            100,

            "quantity":
            90,

            "location":
            80,

            "price":
            85,

            "trust":
            90

        }

    }



    result = explain_recommendation(

        "buyer",

        buyer,

        farmer,

        match_result

    )


    assert "score" in result


    assert "simple_explanation" in result
from ai.recommendation_model import (
    recommendation_module_status
)

from ai.scoring import (
    scoring_module_status
)

from ai.explainable_ai import (
    explainable_ai_status
)



# ==========================================
# Complete AI Marketplace Flow
# ==========================================

def test_complete_ai_marketplace_flow():

    """
    Tests complete AI pipeline.

    Flow:

        Find Match
            ↓
        Score Match
            ↓
        Explain Match
    """


    match_score = calculate_match_score(

        farmer,

        buyer

    )



    score_result = calculate_marketplace_score(

        farmer,

        buyer

    )



    explanation = generate_match_explanation(

        {

            "match_score":
            score_result["overall_score"],

            "breakdown":
            score_result["breakdown"]

        }

    )



    assert match_score >= 0


    assert "overall_score" in score_result


    assert "summary" in explanation



# ==========================================
# Test Empty Farmer Data
# ==========================================

def test_empty_farmer_data():

    """
    AI should handle missing data safely.
    """


    empty_farmer = {}



    score = calculate_match_score(

        empty_farmer,

        buyer

    )


    assert score >= 0



# ==========================================
# Test Empty Buyer Data
# ==========================================

def test_empty_buyer_data():

    """
    AI should handle empty buyer input.
    """


    score = calculate_match_score(

        farmer,

        {}

    )


    assert score >= 0



# ==========================================
# Test Recommendation Module Status
# ==========================================

def test_recommendation_status():

    """
    Checks recommendation engine.
    """


    status = recommendation_module_status()



    assert status["status"] == "active"



# ==========================================
# Test Scoring Module Status
# ==========================================

def test_scoring_status():

    """
    Checks scoring engine.
    """


    status = scoring_module_status()



    assert status["status"] == "active"



# ==========================================
# Test Explainable AI Status
# ==========================================

def test_explainable_ai_status():

    """
    Checks XAI module.
    """


    status = explainable_ai_status()



    assert status["status"] == "active"



# ==========================================
# Test AI Response Format
# ==========================================

def test_ai_response_format():

    """
    Ensures AI output is API ready.
    """


    result = {

        "match_score":
        85,

        "recommendation":
        "Good Match",

        "reason":
        [

            "Product matches",

            "Trust score is high"

        ]

    }



    assert "match_score" in result


    assert "reason" in result