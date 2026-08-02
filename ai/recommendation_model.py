"""
recommendation_model.py
=======================

AgriConnect AI Recommendation Engine.

Purpose:
    - Connect farmers and buyers directly
    - Recommend suitable marketplace matches
    - Improve product discovery

Features:
    - Farmer recommendation
    - Buyer recommendation
    - Product matching
    - Seller ranking
"""


from typing import List, Dict



# ==========================================
# Recommendation Configuration
# ==========================================

MATCH_WEIGHTS = {

    "product_match": 0.35,

    "quantity_match": 0.25,

    "location_match": 0.20,

    "price_match": 0.20

}



# ==========================================
# Product Matching
# ==========================================

def calculate_product_match(
    farmer_product: str,
    buyer_requirement: str
):

    """
    Checks product similarity.
    """


    if (
        farmer_product.lower()
        ==
        buyer_requirement.lower()
    ):

        return 1.0


    return 0.0



# ==========================================
# Quantity Matching
# ==========================================

def calculate_quantity_match(
    available_quantity: float,
    required_quantity: float
):


    """
    Checks quantity compatibility.
    """


    if required_quantity == 0:

        return 0



    difference = abs(
        available_quantity -
        required_quantity
    )



    score = 1 - (
        difference /
        max(
            available_quantity,
            required_quantity
        )
    )


    return max(
        0,
        round(score, 2)
    )



# ==========================================
# Location Matching
# ==========================================

def calculate_location_match(
    farmer_location: str,
    buyer_location: str
):


    """
    Basic location matching.

    Future:
        - GPS distance calculation
        - Maps API
    """


    if (
        farmer_location.lower()
        ==
        buyer_location.lower()
    ):

        return 1.0



    return 0.5
# ==========================================
# Price Matching
# ==========================================

def calculate_price_match(
    farmer_price: float,
    buyer_price: float
):

    """
    Checks whether farmer asking price
    and buyer offer are compatible.
    """


    if farmer_price == 0:

        return 0



    difference = abs(
        farmer_price -
        buyer_price
    )



    score = 1 - (
        difference /
        farmer_price
    )



    return max(
        0,
        round(score, 2)
    )



# ==========================================
# Complete Match Score
# ==========================================

def calculate_match_score(
    farmer: Dict,
    buyer: Dict
):

    """
    Calculates compatibility score
    between farmer and buyer.
    """


    product_score = calculate_product_match(

        farmer.get("product", ""),

        buyer.get("required_product", "")

    )



    quantity_score = calculate_quantity_match(

        farmer.get("quantity", 0),

        buyer.get("required_quantity", 0)

    )



    location_score = calculate_location_match(

        farmer.get("location", ""),

        buyer.get("location", "")

    )



    price_score = calculate_price_match(

        farmer.get("expected_price", 0),

        buyer.get("offered_price", 0)

    )



    final_score = (

        product_score *
        MATCH_WEIGHTS["product_match"]

        +

        quantity_score *
        MATCH_WEIGHTS["quantity_match"]

        +

        location_score *
        MATCH_WEIGHTS["location_match"]

        +

        price_score *
        MATCH_WEIGHTS["price_match"]

    )



    return round(
        final_score * 100,
        2
    )



# ==========================================
# Rank Buyers For Farmer
# ==========================================

def recommend_buyers(
    farmer: Dict,
    buyers: List[Dict]
):

    """
    Returns best buyers for a farmer.
    """


    recommendations = []



    for buyer in buyers:


        score = calculate_match_score(

            farmer,

            buyer

        )


        recommendations.append({

            "buyer_id":
            buyer.get("id"),

            "buyer_name":
            buyer.get("name"),

            "match_score":
            score

        })



    recommendations.sort(

        key=lambda x:
        x["match_score"],

        reverse=True

    )



    return recommendations



# ==========================================
# Rank Farmers For Buyer
# ==========================================

def recommend_farmers(
    buyer: Dict,
    farmers: List[Dict]
):

    """
    Returns best farmers for a buyer.
    """


    recommendations = []



    for farmer in farmers:


        score = calculate_match_score(

            farmer,

            buyer

        )


        recommendations.append({

            "farmer_id":
            farmer.get("id"),

            "farmer_name":
            farmer.get("name"),

            "match_score":
            score

        })



    recommendations.sort(

        key=lambda x:
        x["match_score"],

        reverse=True

    )



    return recommendations
# ==========================================
# Product Similarity
# ==========================================

def calculate_product_similarity(
    product_a: Dict,
    product_b: Dict
):

    """
    Finds similarity between products.

    Future:
        - NLP embeddings
        - Vector similarity model
    """


    score = 0



    if (
        product_a.get("category","").lower()
        ==
        product_b.get("category","").lower()
    ):

        score += 0.5



    if (
        product_a.get("name","").lower()
        ==
        product_b.get("name","").lower()
    ):

        score += 0.5



    return score



# ==========================================
# Recommend Similar Products
# ==========================================

def recommend_similar_products(
    selected_product: Dict,
    products: List[Dict]
):

    """
    Finds products similar to user's selection.
    """


    recommendations = []



    for product in products:


        if (
            product.get("id")
            ==
            selected_product.get("id")
        ):

            continue



        similarity = calculate_product_similarity(

            selected_product,

            product

        )



        if similarity > 0:


            recommendations.append({

                "product_id":
                product.get("id"),

                "product_name":
                product.get("name"),

                "similarity_score":
                round(
                    similarity * 100,
                    2
                )

            })



    recommendations.sort(

        key=lambda x:
        x["similarity_score"],

        reverse=True

    )



    return recommendations



# ==========================================
# Buyer Preference Learning
# ==========================================

def analyze_buyer_preferences(
    purchase_history: List[Dict]
):

    """
    Learns buyer interests from previous
    purchases.

    Future:
        - ML recommendation model
    """


    preferences = {

        "products": [],

        "categories": []

    }



    for item in purchase_history:


        if item.get("product"):

            preferences["products"].append(

                item["product"]

            )



        if item.get("category"):

            preferences["categories"].append(

                item["category"]

            )



    return preferences



# ==========================================
# Personalized Buyer Recommendations
# ==========================================

def personalized_recommendation(
    buyer_preferences: Dict,
    available_products: List[Dict]
):

    """
    Suggests products based on buyer history.
    """


    results = []



    for product in available_products:


        score = 0



        if (
            product.get("name")
            in
            buyer_preferences.get(
                "products",
                []
            )
        ):

            score += 0.7



        if (
            product.get("category")
            in
            buyer_preferences.get(
                "categories",
                []
            )
        ):

            score += 0.3



        if score > 0:


            results.append({

                "product_id":
                product.get("id"),

                "name":
                product.get("name"),

                "recommendation_score":
                round(
                    score * 100,
                    2
                )

            })



    results.sort(

        key=lambda x:
        x["recommendation_score"],

        reverse=True

    )



    return results



# ==========================================
# Recommendation History
# ==========================================

recommendation_history = []



def save_recommendation(
    user_id: int,
    recommendations: List[Dict]
):

    """
    Stores generated recommendations.

    Future:
        Replace with database table.
    """


    recommendation_history.append({

        "user_id":
        user_id,

        "recommendations":
        recommendations

    })



    return True
# ==========================================
# Farmer Ranking System
# ==========================================

def calculate_farmer_rank_score(
    farmer: Dict
):

    """
    Calculates farmer reliability score.

    Factors:
        - Rating
        - Completed orders
        - Response rate
        - Verification status
    """


    rating_score = (
        farmer.get("rating", 0) / 5
    )



    order_score = min(
        farmer.get("completed_orders", 0)
        /
        100,
        1
    )



    response_score = (
        farmer.get("response_rate", 0)
        /
        100
    )



    verification_score = (

        1
        if farmer.get(
            "verified",
            False
        )
        else 0.5

    )



    final_score = (

        rating_score * 0.4

        +

        order_score * 0.2

        +

        response_score * 0.2

        +

        verification_score * 0.2

    )



    return round(
        final_score * 100,
        2
    )



# ==========================================
# Rank Available Farmers
# ==========================================

def rank_farmers(
    farmers: List[Dict]
):

    """
    Orders farmers based on trust
    and marketplace performance.
    """


    ranked = []



    for farmer in farmers:


        score = calculate_farmer_rank_score(

            farmer

        )


        ranked.append({

            "farmer_id":
            farmer.get("id"),

            "farmer_name":
            farmer.get("name"),

            "trust_score":
            score

        })



    ranked.sort(

        key=lambda x:
        x["trust_score"],

        reverse=True

    )



    return ranked



# ==========================================
# ML Recommendation Pipeline
# ==========================================

class RecommendationEngine:

    """
    Future machine learning pipeline.

    Current:
        Rule-based scoring

    Future:
        - Collaborative filtering
        - Neural embeddings
        - Recommendation model
    """



    def __init__(self):

        self.model_name = (
            "AgriConnect Recommendation Engine"
        )



    def prepare_features(
        self,
        farmer: Dict,
        buyer: Dict
    ):

        """
        Converts user data into
        ML features.
        """


        return [

            farmer.get(
                "quantity",
                0
            ),

            buyer.get(
                "required_quantity",
                0
            ),

            calculate_product_match(

                farmer.get(
                    "product",
                    ""
                ),

                buyer.get(
                    "required_product",
                    ""
                )

            ),

            calculate_location_match(

                farmer.get(
                    "location",
                    ""
                ),

                buyer.get(
                    "location",
                    ""
                )

            )

        ]



    def predict_match(
        self,
        farmer: Dict,
        buyer: Dict
    ):

        """
        Predicts compatibility score.
        """


        features = self.prepare_features(

            farmer,

            buyer

        )


        # Placeholder ML prediction

        score = sum(features) / len(features)



        return round(

            score * 100,

            2

        )



# ==========================================
# Create Engine Instance
# ==========================================

recommendation_engine = RecommendationEngine()



# ==========================================
# Database Recommendation Format
# ==========================================

def format_recommendation(
    user_id: int,
    matches: List[Dict]
):

    """
    Creates database-ready output.
    """


    return {

        "user_id":
        user_id,

        "recommendations":

        [

            {

                "target_id":
                item.get("id"),

                "score":
                item.get("score")

            }

            for item in matches

        ]

    }
# ==========================================
# Hybrid Recommendation System
# ==========================================

def hybrid_recommendation(
    farmer: Dict,
    buyer: Dict,
    available_farmers: List[Dict] = None
):

    """
    Combines:

        1. Product matching
        2. Quantity matching
        3. Location matching
        4. Price matching
        5. Farmer trust score

    """



    match_score = calculate_match_score(

        farmer,

        buyer

    )



    result = {

        "match_score":
        match_score

    }



    if available_farmers:


        ranked_farmers = rank_farmers(

            available_farmers

        )


        result["trusted_farmers"] = ranked_farmers[:5]



    return result



# ==========================================
# Recommend Best Marketplace Connections
# ==========================================

def generate_marketplace_recommendations(
    farmers: List[Dict],
    buyers: List[Dict]
):

    """
    Generates farmer-buyer matches.
    """


    matches = []



    for farmer in farmers:


        for buyer in buyers:


            score = calculate_match_score(

                farmer,

                buyer

            )



            if score > 50:


                matches.append({

                    "farmer_id":
                    farmer.get("id"),

                    "buyer_id":
                    buyer.get("id"),

                    "score":
                    score

                })



    matches.sort(

        key=lambda x:
        x["score"],

        reverse=True

    )



    return matches



# ==========================================
# Product Discovery Helper
# ==========================================

def discover_products(
    buyer_preferences: Dict,
    products: List[Dict]
):

    """
    Helps buyers discover products.
    """


    return personalized_recommendation(

        buyer_preferences,

        products

    )



# ==========================================
# Farmer Discovery Helper
# ==========================================

def discover_farmers(
    buyer: Dict,
    farmers: List[Dict]
):

    """
    Helps buyers find suitable farmers.
    """


    recommendations = recommend_farmers(

        buyer,

        farmers

    )


    return recommendations



# ==========================================
# Recommendation Explanation
# ==========================================

def explain_recommendation(
    score: float
):

    """
    Gives human-readable explanation.
    """


    if score >= 85:

        return (
            "Excellent match based on product, "
            "quantity, location and pricing."
        )


    elif score >= 60:

        return (
            "Good match. Some details should "
            "be confirmed before agreement."
        )


    else:

        return (
            "Low match. Consider checking "
            "other options."
        )



# ==========================================
# AI Module Information
# ==========================================

def recommendation_module_status():

    return {

        "module":
        "AgriConnect Recommendation Engine",

        "status":
        "active",

        "purpose":
        "Connect farmers and buyers directly",

        "features":

        [

            "Farmer-Buyer Matching",

            "Product Recommendations",

            "Trust Based Ranking",

            "Price Compatibility",

            "Quantity Matching",

            "Personalized Discovery",

            "ML Ready Pipeline"

        ]

    }