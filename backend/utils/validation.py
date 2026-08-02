"""
validation.py
=============

Validation utilities for AgriConnect.

Handles:
    - User validation
    - Product validation
    - Order validation
    - Payment validation
    - Quotation validation
"""


import re



# ==========================================
# Required Field Validation
# ==========================================

def validate_required_fields(
    data,
    fields
):

    """
    Checks mandatory fields exist.
    """


    missing = []


    for field in fields:

        if (

            field not in data

            or

            data[field] is None

            or

            data[field] == ""

        ):

            missing.append(field)



    return {

        "valid":
        len(missing) == 0,

        "missing":
        missing

    }



# ==========================================
# Email Validation
# ==========================================

def is_valid_email(
    email
):

    """
    Validates email format.
    """


    if not email:

        return False



    pattern = (

        r"^[a-zA-Z0-9._%+-]+"

        r"@"

        r"[a-zA-Z0-9.-]+"

        r"\."

        r"[a-zA-Z]{2,}$"

    )


    return bool(

        re.match(

            pattern,

            email

        )

    )



# ==========================================
# Phone Validation
# ==========================================

def is_valid_phone(
    phone
):

    """
    Validates phone number.
    """


    if not phone:

        return False



    return bool(

        re.match(

            r"^[6-9]\d{9}$",

            str(phone)

        )

    )



# ==========================================
# Password Validation
# ==========================================

def is_valid_password(
    password
):

    """
    Password requirements:

    Minimum:
        8 characters
    """


    if not password:

        return False



    return len(password) >= 8
# ==========================================
# Name Validation
# ==========================================

def is_valid_name(
    name
):

    """
    Checks user name.
    """


    if not name:

        return False



    if len(name.strip()) < 3:

        return False



    return True



# ==========================================
# Farmer Validation
# ==========================================

def validate_farmer_data(
    farmer
):

    """
    Validates farmer registration data.
    """


    required = [

        "name",

        "email",

        "phone",

        "password",

        "location"

    ]



    fields = validate_required_fields(

        farmer,

        required

    )



    if not fields["valid"]:

        return fields



    if not is_valid_email(

        farmer["email"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid email"

        }



    if not is_valid_phone(

        farmer["phone"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid phone"

        }



    return {

        "valid":
        True

    }



# ==========================================
# Customer Validation
# ==========================================

def validate_customer_data(
    customer
):

    """
    Validates customer registration.
    """


    required = [

        "name",

        "email",

        "phone",

        "password"

    ]



    fields = validate_required_fields(

        customer,

        required

    )



    if not fields["valid"]:

        return fields



    return {

        "valid":
        is_valid_email(

            customer["email"]

        )

    }



# ==========================================
# Price Validation
# ==========================================

def is_valid_price(
    price
):

    """
    Validates product price.
    """


    try:

        return float(price) > 0


    except:

        return False



# ==========================================
# Quantity Validation
# ==========================================

def is_valid_quantity(
    quantity
):

    """
    Validates product quantity.
    """


    try:

        return int(quantity) > 0


    except:

        return False



# ==========================================
# Product Validation
# ==========================================

def validate_product_data(
    product
):

    """
    Validates marketplace product.
    """


    required = [

        "name",

        "category",

        "quantity",

        "price"

    ]



    result = validate_required_fields(

        product,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_quantity(

        product["quantity"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid quantity"

        }



    if not is_valid_price(

        product["price"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid price"

        }



    return {

        "valid":
        True

    }
# ==========================================
# Quotation Validation
# ==========================================

def validate_quotation_data(
    quotation
):

    """
    Validates farmer quotation.
    """


    required = [

        "buyer_id",

        "product_id",

        "quantity",

        "price_per_unit"

    ]



    result = validate_required_fields(

        quotation,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_quantity(

        quotation["quantity"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid quotation quantity"

        }



    if not is_valid_price(

        quotation["price_per_unit"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid quotation price"

        }



    return {

        "valid":
        True

    }



# ==========================================
# Order Validation
# ==========================================

def validate_order_data(
    order
):

    """
    Validates order creation.
    """


    required = [

        "product_id",

        "quantity",

        "customer_id"

    ]



    result = validate_required_fields(

        order,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_quantity(

        order["quantity"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid order quantity"

        }



    return {

        "valid":
        True

    }



# ==========================================
# Order Status Validation
# ==========================================

def is_valid_order_status(
    status
):

    """
    Checks order lifecycle status.
    """


    allowed = [

        "pending",

        "confirmed",

        "processing",

        "shipped",

        "delivered",

        "cancelled"

    ]



    return status in allowed



# ==========================================
# Payment Validation
# ==========================================

def validate_payment_data(
    payment
):

    """
    Validates payment information.
    """


    required = [

        "order_id",

        "amount",

        "payment_method"

    ]



    result = validate_required_fields(

        payment,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_price(

        payment["amount"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid payment amount"

        }



    return {

        "valid":
        True

    }



# ==========================================
# Payment Status Validation
# ==========================================

def is_valid_payment_status(
    status
):

    """
    Payment status validation.
    """


    allowed = [

        "pending",

        "paid",

        "failed",

        "refund_requested",

        "refunded"

    ]



    return status in allowed



# ==========================================
# Review Validation
# ==========================================

def validate_review_data(
    review
):

    """
    Validates customer review.
    """


    required = [

        "product_id",

        "rating",

        "comment"

    ]



    result = validate_required_fields(

        review,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_rating(

        review["rating"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid rating"

        }



    return {

        "valid":
        True

    }



# ==========================================
# Rating Validation
# ==========================================

def is_valid_rating(
    rating
):

    """
    Rating should be between 1 and 5.
    """


    try:

        return (

            1 <= int(rating) <= 5

        )


    except:

        return False
# ==========================================
# Role Validation
# ==========================================

def is_valid_role(
    role
):

    """
    Checks AgriConnect user roles.
    """


    allowed_roles = [

        "farmer",

        "customer",

        "admin"

    ]


    return role in allowed_roles



# ==========================================
# Login Validation
# ==========================================

def validate_login_data(
    login
):

    """
    Validates login request.
    """


    required = [

        "email",

        "password"

    ]



    result = validate_required_fields(

        login,

        required

    )



    if not result["valid"]:

        return result



    if not is_valid_email(

        login["email"]

    ):

        return {

            "valid":
            False,

            "error":
            "Invalid email format"

        }



    return {

        "valid":
        True

    }



# ==========================================
# User Role Permission
# ==========================================

def check_permission(
    user_role,
    required_role
):

    """
    Checks whether user has permission.
    """


    if user_role == "admin":

        return True



    return user_role == required_role



# ==========================================
# File Extension Validation
# ==========================================

def is_valid_file_type(
    filename,
    allowed_types
):

    """
    Validates uploaded file types.
    """


    if not filename:

        return False



    extension = filename.split(

        "."

    )[-1].lower()



    return extension in allowed_types



# ==========================================
# Image Upload Validation
# ==========================================

def is_valid_image(
    filename
):

    """
    Allows product/farmer images.
    """


    image_types = [

        "jpg",

        "jpeg",

        "png",

        "webp"

    ]



    return is_valid_file_type(

        filename,

        image_types

    )



# ==========================================
# Text Security Validation
# ==========================================

def contains_safe_text(
    text
):

    """
    Basic protection against
    unsafe input patterns.
    """


    if not text:

        return True



    blocked_patterns = [

        "<script",

        "javascript:",

        "DROP TABLE",

        "SELECT * FROM"

    ]



    lower_text = text.lower()



    for pattern in blocked_patterns:

        if pattern.lower() in lower_text:

            return False



    return True



# ==========================================
# Sanitize Text Input
# ==========================================

def sanitize_text(
    text
):

    """
    Removes unwanted characters.
    """


    if not text:

        return ""



    return (

        text

        .replace(

            "<",

            ""

        )

        .replace(

            ">",

            ""

        )

        .strip()

    )
from datetime import datetime



# ==========================================
# Location Validation
# ==========================================

def is_valid_location(
    location
):

    """
    Validates user location.
    """


    if not location:

        return False



    return len(

        location.strip()

    ) >= 2



# ==========================================
# Product Availability Validation
# ==========================================

def is_product_available(
    quantity,
    requested_quantity
):

    """
    Checks available stock.
    """


    try:

        return (

            int(quantity)

            >=

            int(requested_quantity)

        )


    except:

        return False



# ==========================================
# Price Range Validation
# ==========================================

def is_reasonable_price(
    price,
    minimum=1,
    maximum=1000000
):

    """
    Prevents invalid marketplace prices.
    """


    try:

        value = float(price)


        return (

            minimum

            <=

            value

            <=

            maximum

        )


    except:

        return False



# ==========================================
# Quantity Limit Validation
# ==========================================

def is_reasonable_quantity(
    quantity
):

    """
    Checks marketplace quantity limits.
    """


    try:

        value = int(quantity)


        return (

            1

            <=

            value

            <=

            100000

        )


    except:

        return False



# ==========================================
# Transaction Validation
# ==========================================

def validate_transaction(
    farmer_id,
    buyer_id,
    product_id
):

    """
    Checks transaction relationship.
    """


    if not farmer_id:

        return False



    if not buyer_id:

        return False



    if not product_id:

        return False



    return True



# ==========================================
# Date Validation
# ==========================================

def is_valid_date(
    date_value
):

    """
    Validates date format.
    """


    try:

        if isinstance(

            date_value,

            datetime

        ):

            return True



        datetime.strptime(

            str(date_value),

            "%Y-%m-%d"

        )


        return True


    except:

        return False



# ==========================================
# Contact Availability Check
# ==========================================

def validate_contact_information(
    email,
    phone
):

    """
    Validates communication details.
    """


    return (

        is_valid_email(email)

        and

        is_valid_phone(phone)

    )



# ==========================================
# Validation Module Status
# ==========================================

def validation_status():

    return {

        "module":

        "AgriConnect Validation System",


        "status":

        "active",


        "features":

        [

            "User Validation",

            "Product Validation",

            "Quotation Validation",

            "Order Validation",

            "Payment Validation",

            "Review Validation",

            "Security Checks",

            "Business Rules"

        ]

    }