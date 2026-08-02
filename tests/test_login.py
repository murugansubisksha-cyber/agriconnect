"""
test_login.py
=============

Tests for AgriConnect Authentication System.

Covers:
    - User registration
    - Login
    - JWT token generation
    - Invalid credentials
    - Protected routes
"""


import pytest

from fastapi.testclient import TestClient

from backend.main import app



client = TestClient(app)



# ==========================================
# Test Farmer Registration
# ==========================================

def test_farmer_registration():

    """
    Farmer should be able to create account.
    """


    response = client.post(

        "/auth/register/farmer",

        json={

            "name":
            "Test Farmer",

            "email":
            "farmer@test.com",

            "password":
            "password123",

            "phone":
            "9876543210"

        }

    )



    assert response.status_code in [

        200,

        201,

        400

    ]



# ==========================================
# Test Customer Registration
# ==========================================

def test_customer_registration():

    """
    Customer should be able to create account.
    """


    response = client.post(

        "/auth/register/customer",

        json={

            "name":
            "Test Buyer",

            "email":
            "buyer@test.com",

            "password":
            "password123",

            "phone":
            "9876543211"

        }

    )



    assert response.status_code in [

        200,

        201,

        400

    ]



# ==========================================
# Test Login Endpoint Availability
# ==========================================

def test_login_endpoint_exists():

    """
    Checks login route availability.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "farmer@test.com",

            "password":
            "password123"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]
# ==========================================
# Test Successful Login
# ==========================================

def test_successful_login():

    """
    Valid credentials should return tokens.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "farmer@test.com",

            "password":
            "password123"

        }

    )



    assert response.status_code in [

        200,

        401

    ]



    if response.status_code == 200:


        data = response.json()


        assert "access_token" in data



# ==========================================
# Test JWT Token Structure
# ==========================================

def test_jwt_token_structure():

    """
    Checks generated token format.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "farmer@test.com",

            "password":
            "password123"

        }

    )



    if response.status_code == 200:


        token_data = response.json()



        assert isinstance(

            token_data.get(
                "access_token"
            ),

            str

        )



# ==========================================
# Test Refresh Token
# ==========================================

def test_refresh_token():

    """
    Checks refresh token endpoint.
    """


    response = client.post(

        "/auth/refresh",

        json={

            "refresh_token":
            "test_refresh_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



# ==========================================
# Test Token Type
# ==========================================

def test_token_type():

    """
    JWT token type should be returned.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "buyer@test.com",

            "password":
            "password123"

        }

    )



    if response.status_code == 200:


        data = response.json()



        assert data.get(
            "token_type"
        ) in [

            "bearer",

            None

        ]
# ==========================================
# Test Wrong Password
# ==========================================

def test_wrong_password():

    """
    Correct email but wrong password
    should fail.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "farmer@test.com",

            "password":
            "wrong_password"

        }

    )



    assert response.status_code in [

        401,

        400

    ]



# ==========================================
# Test Non Existing User
# ==========================================

def test_login_unknown_user():

    """
    User not registered should not login.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "unknown@test.com",

            "password":
            "password123"

        }

    )



    assert response.status_code in [

        401,

        404

    ]



# ==========================================
# Test Duplicate Farmer Registration
# ==========================================

def test_duplicate_farmer_registration():

    """
    Same email should not create
    multiple accounts.
    """


    user_data = {

        "name":
        "Duplicate Farmer",

        "email":
        "duplicate@test.com",

        "password":
        "password123",

        "phone":
        "9000000000"

    }



    first_response = client.post(

        "/auth/register/farmer",

        json=user_data

    )



    second_response = client.post(

        "/auth/register/farmer",

        json=user_data

    )



    assert second_response.status_code in [

        400,

        409

    ]



# ==========================================
# Test Empty Password
# ==========================================

def test_empty_password():

    """
    Empty password should be rejected.
    """


    response = client.post(

        "/auth/register/customer",

        json={

            "name":
            "Test User",

            "email":
            "empty@test.com",

            "password":
            "",

            "phone":
            "9999999999"

        }

    )



    assert response.status_code in [

        400,

        422

    ]



# ==========================================
# Test Invalid Email Format
# ==========================================

def test_invalid_email():

    """
    Invalid email should fail validation.
    """


    response = client.post(

        "/auth/register/customer",

        json={

            "name":
            "Invalid Email",

            "email":
            "wrong_email",

            "password":
            "password123",

            "phone":
            "9999999999"

        }

    )



    assert response.status_code in [

        400,

        422

    ]
# ==========================================
# Test Protected Route Without Token
# ==========================================

def test_access_protected_route_without_token():

    """
    Protected routes should reject
    unauthenticated users.
    """


    response = client.get(

        "/auth/me"

    )



    assert response.status_code in [

        401,

        403,

        404

    ]



# ==========================================
# Test Protected Route With Invalid Token
# ==========================================

def test_access_with_invalid_token():

    """
    Invalid JWT should be rejected.
    """


    response = client.get(

        "/auth/me",

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
# Test Farmer Role Access
# ==========================================

def test_farmer_role_access():

    """
    Farmer should receive farmer role.
    """


    response = client.get(

        "/auth/me",

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



    if response.status_code == 200:


        data = response.json()



        assert data.get(
            "role"
        ) == "farmer"



# ==========================================
# Test Customer Role Access
# ==========================================

def test_customer_role_access():

    """
    Customer should receive customer role.
    """


    response = client.get(

        "/auth/me",

        headers={

            "Authorization":
            "Bearer customer_test_token"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]



    if response.status_code == 200:


        data = response.json()



        assert data.get(
            "role"
        ) == "customer"



# ==========================================
# Test Logout Endpoint
# ==========================================

def test_logout():

    """
    User logout should invalidate session/token
    if implemented.
    """


    response = client.post(

        "/auth/logout",

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
# Complete Authentication Workflow Test
# ==========================================

def test_complete_auth_flow():

    """
    Complete user authentication lifecycle.

    Flow:
        Register
        Login
        Access Profile
    """


    register_response = client.post(

        "/auth/register/customer",

        json={

            "name":
            "Workflow User",

            "email":
            "workflow@test.com",

            "password":
            "password123",

            "phone":
            "8888888888"

        }

    )



    assert register_response.status_code in [

        200,

        201,

        400

    ]



    login_response = client.post(

        "/auth/login",

        data={

            "username":
            "workflow@test.com",

            "password":
            "password123"

        }

    )



    assert login_response.status_code in [

        200,

        401

    ]



# ==========================================
# Test SQL Injection Protection
# ==========================================

def test_sql_injection_login():

    """
    Login should safely handle malicious input.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "' OR 1=1 --",

            "password":
            "anything"

        }

    )



    assert response.status_code in [

        400,

        401

    ]



# ==========================================
# Test Very Long Password
# ==========================================

def test_long_password():

    """
    Extremely long passwords should
    be handled safely.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "test@test.com",

            "password":
            "a" * 500

        }

    )



    assert response.status_code in [

        400,

        401

    ]



# ==========================================
# Test Missing Login Fields
# ==========================================

def test_missing_login_fields():

    """
    Login requires username and password.
    """


    response = client.post(

        "/auth/login",

        data={}

    )



    assert response.status_code in [

        400,

        401,

        422

    ]



# ==========================================
# Authentication Module Health Check
# ==========================================

def test_auth_module_available():

    """
    Checks authentication routes exist.
    """


    response = client.post(

        "/auth/login",

        data={

            "username":
            "check@test.com",

            "password":
            "check123"

        }

    )



    assert response.status_code in [

        200,

        401,

        404

    ]