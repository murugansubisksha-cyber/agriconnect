"""
helpers.py
==========

Common helper functions for AgriConnect.

Contains:
    - Response formatting
    - Validation helpers
    - Date/time helpers
    - Text processing
    - Common utilities
"""


from datetime import datetime

import uuid



# ==========================================
# Generate Unique ID
# ==========================================

def generate_unique_id():

    """
    Generates unique transaction/reference ID.
    """


    return str(uuid.uuid4())



# ==========================================
# Current Timestamp
# ==========================================

def get_current_timestamp():

    """
    Returns current server timestamp.
    """


    return datetime.utcnow()



# ==========================================
# Success Response Formatter
# ==========================================

def success_response(
    message,
    data=None
):

    """
    Standard API success response.
    """


    return {

        "success":
        True,

        "message":
        message,

        "data":
        data

    }



# ==========================================
# Error Response Formatter
# ==========================================

def error_response(
    message,
    error_code=None
):

    """
    Standard API error response.
    """


    return {

        "success":
        False,

        "message":
        message,

        "error_code":
        error_code

    }



# ==========================================
# Clean Text Input
# ==========================================

def clean_text(
    text
):

    """
    Removes unnecessary spaces.
    """


    if not text:

        return ""


    return text.strip()
import re



# ==========================================
# Email Validation
# ==========================================

def validate_email(
    email
):

    """
    Checks whether email format is valid.
    """


    if not email:

        return False



    pattern = (

        r"^[\w\.-]+@[\w\.-]+\.\w+$"

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

def validate_phone(
    phone
):

    """
    Validates Indian-style phone numbers.
    """


    if not phone:

        return False



    pattern = (

        r"^[6-9]\d{9}$"

    )


    return bool(

        re.match(

            pattern,

            phone

        )

    )



# ==========================================
# Password Validation
# ==========================================

def validate_password(
    password
):

    """
    Basic password security check.

    Requirements:
        - Minimum 8 characters
    """


    if not password:

        return False



    if len(password) < 8:

        return False



    return True



# ==========================================
# Positive Number Validation
# ==========================================

def validate_positive_number(
    value
):

    """
    Checks positive numeric values.

    Used for:
        - Price
        - Quantity
        - Amount
    """


    try:

        return float(value) > 0


    except:

        return False



# ==========================================
# Safe Integer Conversion
# ==========================================

def safe_int(
    value,
    default=0
):

    """
    Converts value to integer safely.
    """


    try:

        return int(value)


    except:

        return default



# ==========================================
# Safe Float Conversion
# ==========================================

def safe_float(
    value,
    default=0.0
):

    """
    Converts value to float safely.
    """


   
try:

        return float(value)


    except:

        return default
# ==========================================
# Pagination Helper
# ==========================================

def paginate(
    items,
    page=1,
    limit=10
):

    """
    Returns paginated data.

    Used for:
        - Products
        - Orders
        - Quotations
        - Reviews
    """


    if page < 1:

        page = 1


    if limit < 1:

        limit = 10



    start = (

        page - 1

    ) * limit



    end = start + limit



    return {

        "page":
        page,

        "limit":
        limit,

        "total":
        len(items),

        "data":
        items[start:end]

    }



# ==========================================
# Search Text Helper
# ==========================================

def search_match(
    text,
    keyword
):

    """
    Checks whether keyword exists
    in text.
    """


    if not text or not keyword:

        return False



    return (

        keyword.lower()

        in

        text.lower()

    )



# ==========================================
# Sort List Data
# ==========================================

def sort_data(
    data,
    key,
    reverse=False
):

    """
    Sorts list of dictionaries.
    """


    try:

        return sorted(

            data,

            key=lambda x:

            x.get(
                key,
                ""
            ),

            reverse=reverse

        )


    except Exception:

        return data



# ==========================================
# Mask Phone Number
# ==========================================

def mask_phone(
    phone
):

    """
    Hides phone number partially.

    Example:
        9876543210
        98765*****
    """


    if not phone:

        return None



    if len(phone) < 5:

        return phone



    return (

        phone[:5]

        +

        "*" *

        (

            len(phone)-5

        )

    )



# ==========================================
# Mask Email
# ==========================================

def mask_email(
    email
):

    """
    Protects user email privacy.
    """


    if not email or "@" not in email:

        return email



    username, domain = email.split(

        "@"

    )



    if len(username) <= 2:

        masked = "*"


    else:

        masked = (

            username[0]

            +

            "*" *

            (

                len(username)-2

            )

            +

            username[-1]

        )



    return (

        masked

        +

        "@"

        +

        domain

    )
# ==========================================
# Allowed Roles Validation
# ==========================================

def validate_role(
    role
):

    """
    Checks valid AgriConnect roles.
    """


    allowed_roles = [

        "farmer",

        "customer",

        "admin"

    ]


    return role in allowed_roles



# ==========================================
# Status Validation
# ==========================================

def validate_status(
    status,
    allowed_statuses
):

    """
    Checks whether status is allowed.
    """


    return status in allowed_statuses



# ==========================================
# Product Status Validation
# ==========================================

def validate_product_status(
    status
):

    """
    Product lifecycle status.
    """


    allowed = [

        "available",

        "sold",

        "inactive"

    ]


    return status in allowed



# ==========================================
# Order Status Validation
# ==========================================

def validate_order_status(
    status
):

    """
    Order lifecycle validation.
    """


    allowed = [

        "pending",

        "confirmed",

        "processing",

        "completed",

        "cancelled"

    ]


    return status in allowed



# ==========================================
# File Extension Validation
# ==========================================

def validate_file_extension(
    filename,
    allowed_extensions
):

    """
    Checks uploaded file type.
    """


    if not filename:

        return False



    extension = filename.split(

        "."

    )[-1].lower()



    return extension in allowed_extensions



# ==========================================
# Image Validation
# ==========================================

def validate_image_file(
    filename
):

    """
    Checks image uploads.
    """


    allowed_images = [

        "jpg",

        "jpeg",

        "png",

        "webp"

    ]



    return validate_file_extension(

        filename,

        allowed_images

    )



# ==========================================
# File Size Validation
# ==========================================

def validate_file_size(
    size_in_bytes,
    max_size_mb=5
):

    """
    Prevents large uploads.
    """


    max_bytes = (

        max_size_mb

        *

        1024

        *

        1024

    )



    return size_in_bytes <= max_bytes



# ==========================================
# Location Match Helper
# ==========================================

def same_location(
    location1,
    location2
):

    """
    Checks whether two users
    are from same location.
    """


    if not location1 or not location2:

        return False



    return (

        location1.lower()

        ==

        location2.lower()

    )
# ==========================================
# Currency Formatter
# ==========================================

def format_currency(
    amount
):

    """
    Formats amount for display.

    Example:
        2500
        ₹2,500
    """


    try:

        return (

            "₹"

            +

            format(

                float(amount),

                ",.2f"

            )

        )


    except:

        return "₹0.00"



# ==========================================
# Calculate Percentage
# ==========================================

def calculate_percentage(
    value,
    total
):

    """
    Calculates percentage safely.
    """


    if not total:

        return 0



    return round(

        (

            value / total

        )

        *

        100,

        2

    )



# ==========================================
# Remove Empty Values
# ==========================================

def remove_empty_values(
    data
):

    """
    Removes empty fields from dictionary.
    """


    if not isinstance(

        data,

        dict

    ):

        return data



    return {

        key: value

        for key, value in data.items()

        if value not in [

            None,

            "",

            []

        ]

    }



# ==========================================
# Filter Dictionary Keys
# ==========================================

def filter_dict(
    data,
    keys
):

    """
    Returns only required fields.
    """


    return {

        key:

        data.get(key)

        for key in keys

        if key in data

    }



# ==========================================
# Distance Approximation Helper
# ==========================================

def calculate_distance(
    location1,
    location2
):

    """
    Basic location comparison.

    Future:
        GPS based distance calculation.
    """


    if same_location(

        location1,

        location2

    ):

        return 0



    return None



# ==========================================
# Generate Reference Code
# ==========================================

def generate_reference_code(
    prefix="AGR"
):

    """
    Creates reference IDs.

    Used for:
        - Orders
        - Payments
        - Quotations
    """


    unique_part = str(uuid.uuid4())[:8]


    return (

        prefix

        +

        "_"

        +

        unique_part.upper()

    )



# ==========================================
# Utility Module Status
# ==========================================

def helpers_status():

    return {

        "module":

        "AgriConnect Utility Helpers",


        "status":

        "active",


        "features":

        [

            "Validation Helpers",

            "Response Formatting",

            "Pagination",

            "Search Utilities",

            "Privacy Masking",

            "File Validation",

            "Status Checking",

            "Reference Generation"

        ]

    }