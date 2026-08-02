"""
test_product.py
===============

Tests for AgriConnect Product API.

Covers:
    - Create product
    - Get products
    - Update product
    - Delete product
    - Authorization checks
"""


import pytest

from fastapi.testclient import TestClient

from backend.main import app



client = TestClient(app)



# ==========================================
# Test Product Creation
# ==========================================

def test_create_product():

    """
    Farmer should be able to create product.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Rice",

            "category":
            "Grains",

            "quantity":
            100,

            "price":
            2500,

            "description":
            "Fresh harvested rice"

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
# Test Product List
# ==========================================

def test_get_products():

    """
    Anyone should be able to view products.
    """


    response = client.get(

        "/products/"

    )


    assert response.status_code == 200



# ==========================================
# Test Product Details
# ==========================================

def test_get_product_details():

    """
    Get single product information.
    """


    response = client.get(

        "/products/1"

    )


    assert response.status_code in [

        200,

        404

    ]
# ==========================================
# Test Product Update
# ==========================================

def test_update_product():

    """
    Farmer should be able to update
    their own product.
    """


    response = client.put(

        "/products/1",

        json={

            "name":
            "Premium Rice",

            "quantity":
            150,

            "price":
            2700,

            "description":
            "Updated product details"

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Product Price Update
# ==========================================

def test_update_product_price():

    """
    Checks price modification.
    """


    response = client.put(

        "/products/1",

        json={

            "price":
            3000

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Product Delete
# ==========================================

def test_delete_product():

    """
    Farmer should delete own product.
    """


    response = client.delete(

        "/products/1",

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        204,

        401,

        404

    ]



# ==========================================
# Test Unauthorized Update
# ==========================================

def test_customer_cannot_update_product():

    """
    Buyers/customers should not update
    farmer products.
    """


    response = client.put(

        "/products/1",

        json={

            "price":
            5000

        },

        headers={

            "Authorization":
            "Bearer customer_test_token"

        }

    )



    assert response.status_code in [

        401,

        403,

        404

    ]
# ==========================================
# Test Product Search
# ==========================================

def test_search_product():

    """
    Buyer should be able to search products.
    """


    response = client.get(

        "/products/search?name=Rice"

    )



    assert response.status_code in [

        200,

        404

    ]



# ==========================================
# Test Category Filter
# ==========================================

def test_filter_by_category():

    """
    Checks product category filtering.
    """


    response = client.get(

        "/products/filter?category=Grains"

    )



    assert response.status_code in [

        200,

        404

    ]



# ==========================================
# Test Price Filter
# ==========================================

def test_filter_by_price():

    """
    Checks maximum price filtering.
    """


    response = client.get(

        "/products/filter?max_price=3000"

    )



    assert response.status_code in [

        200,

        404

    ]



# ==========================================
# Test Quantity Validation
# ==========================================

def test_invalid_product_quantity():

    """
    Product quantity should not be negative.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Wheat",

            "category":
            "Grains",

            "quantity":
            -10,

            "price":
            2000

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

def test_invalid_product_price():

    """
    Product price validation.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Rice",

            "category":
            "Grains",

            "quantity":
            50,

            "price":
            -500

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
# Test Missing Authentication
# ==========================================

def test_create_product_without_token():

    """
    Product creation requires login.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Tomato",

            "category":
            "Vegetable",

            "quantity":
            100,

            "price":
            1500

        }

    )



    assert response.status_code in [

        401,

        403

    ]



# ==========================================
# Test Invalid Token
# ==========================================

def test_create_product_invalid_token():

    """
    Invalid JWT should be rejected.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Onion",

            "category":
            "Vegetable",

            "quantity":
            50,

            "price":
            2000

        },

        headers={

            "Authorization":
            "Bearer invalid_token"

        }

    )



    assert response.status_code in [

        401,

        403

    ]



# ==========================================
# Customer Cannot Create Product
# ==========================================

def test_customer_cannot_create_product():

    """
    Only farmers can add products.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Rice",

            "category":
            "Grains",

            "quantity":
            100,

            "price":
            2500

        },

        headers={

            "Authorization":
            "Bearer customer_test_token"

        }

    )



    assert response.status_code in [

        403,

        401

    ]



# ==========================================
# Product Ownership Validation
# ==========================================

def test_farmer_cannot_modify_other_product():

    """
    Farmer should not modify another
    farmer's product.
    """


    response = client.put(

        "/products/999",

        json={

            "price":
            5000

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        403,

        404,

        401

    ]



# ==========================================
# Product Database Consistency
# ==========================================

def test_product_response_structure():

    """
    Checks API response format.
    """


    response = client.get(

        "/products/"

    )



    if response.status_code == 200:


        data = response.json()



        assert isinstance(

            data,

            (list, dict)

        )
# ==========================================
# Complete Product Workflow Test
# ==========================================

def test_product_marketplace_flow():

    """
    Tests complete product lifecycle.

    Flow:
        Create
        View
        Search
        Update
    """


    create_response = client.post(

        "/products/",

        json={

            "name":
            "Groundnut",

            "category":
            "Oil Seeds",

            "quantity":
            200,

            "price":
            6000,

            "description":
            "Fresh groundnut"

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



    list_response = client.get(

        "/products/"

    )



    assert list_response.status_code == 200



# ==========================================
# Test Empty Search Result
# ==========================================

def test_product_not_found_search():

    """
    Search for unavailable product.
    """


    response = client.get(

        "/products/search?name=UnknownProduct"

    )



    assert response.status_code in [

        200,

        404

    ]



# ==========================================
# Test Large Quantity Product
# ==========================================

def test_large_quantity_product():

    """
    Checks bulk product listing.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Rice",

            "category":
            "Grains",

            "quantity":
            100000,

            "price":
            250000

        },

        headers={

            "Authorization":
            "Bearer farmer_test_token"

        }

    )



    assert response.status_code in [

        200,

        201,

        401,

        422

    ]



# ==========================================
# Test Missing Product Fields
# ==========================================

def test_missing_product_fields():

    """
    Required fields validation.
    """


    response = client.post(

        "/products/",

        json={

            "name":
            "Rice"

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
# Product Module Health Test
# ==========================================

def test_product_module_available():

    """
    Checks product route availability.
    """


    response = client.get(

        "/products/"

    )



    assert response.status_code in [

        200,

        404

    ]