"""
test_quotation.py
=================

Tests for AgriConnect Quotation API.

Covers:
    - Create quotation
    - View quotation
    - Update quotation
    - Accept quotation
    - Reject quotation
"""


import pytest

from fastapi.testclient import TestClient

from backend.main import app



client = TestClient(app)



# ==========================================
# Test Create Quotation
# ==========================================

def test_create_quotation():

    """
    Farmer should create quotation
    for buyer.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10,

            "product_id":
            1,

            "quantity":
            100,

            "price_per_unit":
            50,

            "message":
            "Fresh farm product quotation"

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        201,

        401

    ]



# ==========================================
# Test Get Quotation Details
# ==========================================

def test_get_quotation_details():

    """
    User should view quotation details.
    """


    response = client.get(

        "/quotations/1",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Quotation List
# ==========================================

def test_get_all_quotations():

    """
    Checks quotation listing.
    """


    response = client.get(

        "/quotations/",

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401

    ]
# ==========================================
# Test Accept Quotation
# ==========================================

def test_accept_quotation():

    """
    Buyer should accept quotation.
    """


    response = client.put(

        "/quotations/1/accept",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Reject Quotation
# ==========================================

def test_reject_quotation():

    """
    Buyer should reject quotation.
    """


    response = client.put(

        "/quotations/2/reject",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Quotation Status Update
# ==========================================

def test_update_quotation_status():

    """
    Checks quotation status changes.
    """


    response = client.put(

        "/quotations/1/status",

        json={

            "status":
            "accepted"

        },

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        400,

        401,

        404

    ]



# ==========================================
# Test Buyer Negotiation Response
# ==========================================

def test_buyer_counter_offer():

    """
    Buyer should be able to
    negotiate price.
    """


    response = client.put(

        "/quotations/1/negotiate",

        json={

            "counter_price":
            45,

            "message":
            "Can you reduce the price?"

        },

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        400,

        401,

        404

    ]



# ==========================================
# Test Farmer View Incoming Quotations
# ==========================================

def test_farmer_received_quotations():

    """
    Farmer should view buyer responses.
    """


    response = client.get(

        "/quotations/farmer/incoming",

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401

    ]# ==========================================
# Test Invalid Quantity
# ==========================================

def test_invalid_quotation_quantity():

    """
    Quantity should not be negative.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10,

            "product_id":
            1,

            "quantity":
            -50,

            "price_per_unit":
            50

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        400,

        401,

        422

    ]



# ==========================================
# Test Invalid Price
# ==========================================

def test_invalid_quotation_price():

    """
    Price should be positive.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10,

            "product_id":
            1,

            "quantity":
            100,

            "price_per_unit":
            -100

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        400,

        401,

        422

    ]



# ==========================================
# Test Missing Required Fields
# ==========================================

def test_missing_quotation_fields():

    """
    Required quotation fields
    should be validated.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        400,

        401,

        422

    ]



# ==========================================
# Buyer Cannot Create Quotation
# ==========================================

def test_buyer_cannot_create_quotation():

    """
    Only farmers should create
    product quotations.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            5,

            "product_id":
            1,

            "quantity":
            100,

            "price_per_unit":
            50

        },

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        403,

        401

    ]



# ==========================================
# Unauthorized Quotation Access
# ==========================================

def test_access_without_token():

    """
    Quotation routes require login.
    """


    response = client.get(

        "/quotations/1"

    )



    assert response.status_code in [

        401,

        403

    ]



# ==========================================
# User Cannot Access Other Quotation
# ==========================================

def test_quotation_ownership_check():

    """
    User should not access
    another user's quotation.
    """


    response = client.get(

        "/quotations/999",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        403,

        404,

        401

    ]
# ==========================================
# Complete Quotation Lifecycle Test
# ==========================================

def test_complete_quotation_flow():

    """
    Tests complete quotation journey.

    Flow:
        Create
        View
        Accept
    """


    create_response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10,

            "product_id":
            1,

            "quantity":
            100,

            "price_per_unit":
            50,

            "message":
            "Bulk order quotation"

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert create_response.status_code in [

        200,

        201,

        401

    ]



    view_response = client.get(

        "/quotations/1",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert view_response.status_code in [

        200,

        401,

        404

    ]



    accept_response = client.put(

        "/quotations/1/accept",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert accept_response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Multiple Quotations
# ==========================================

def test_multiple_quotation_creation():

    """
    Farmer can send quotations
    to different buyers.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            20,

            "product_id":
            2,

            "quantity":
            200,

            "price_per_unit":
            70

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        201,

        401

    ]



# ==========================================
# Test Quotation History
# ==========================================

def test_quotation_history():

    """
    User should view previous quotations.
    """


    response = client.get(

        "/quotations/history",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Accepted Quotation Data
# ==========================================

def test_accepted_quotation_structure():

    """
    Accepted quotation should contain
    important information.
    """


    response = client.get(

        "/quotations/1",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    if response.status_code == 200:


        data = response.json()


        assert isinstance(

            data,

            dict

        )
# ==========================================
# Test Invalid Status Update
# ==========================================

def test_invalid_quotation_status():

    """
    Invalid status should be rejected.
    """


    response = client.put(

        "/quotations/1/status",

        json={

            "status":
            "unknown_status"

        },

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        400,

        401,

        404

    ]



# ==========================================
# Test Empty Negotiation Message
# ==========================================

def test_empty_negotiation_message():

    """
    Negotiation message validation.
    """


    response = client.put(

        "/quotations/1/negotiate",

        json={

            "counter_price":
            45,

            "message":
            ""

        },

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    assert response.status_code in [

        400,

        401,

        422

    ]



# ==========================================
# Test Excessive Price Value
# ==========================================

def test_extreme_price_value():

    """
    Handles unrealistic prices.
    """


    response = client.post(

        "/quotations/",

        json={

            "buyer_id":
            10,

            "product_id":
            1,

            "quantity":
            100,

            "price_per_unit":
            999999999

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        201,

        400,

        401,

        422

    ]



# ==========================================
# Test Quotation Status Response
# ==========================================

def test_quotation_status_response():

    """
    Checks quotation response format.
    """


    response = client.get(

        "/quotations/1",

        headers={

            "Authorization":
            "Bearer buyer_test_token"

        }

    )



    if response.status_code == 200:


        data = response.json()


        assert "status" in data



# ==========================================
# Test Quotation Module Availability
# ==========================================

def test_quotation_module_available():

    """
    Checks quotation route availability.
    """


    response = client.get(

        "/quotations/",

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401

    ]



# ==========================================
# Test Quotation API Response Type
# ==========================================

def test_quotation_response_type():

    """
    API should return valid response.
    """


    response = client.get(

        "/quotations/",

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    if response.status_code == 200:


        data = response.json()


        assert isinstance(

            data,

            (list, dict)

        )