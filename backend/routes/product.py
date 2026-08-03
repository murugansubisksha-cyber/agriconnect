"""
product.py
==========
Product Management Routes for AgriConnect

Handles:
 - Add Product
 - View Products
 - Update Product
 - Delete Product (Soft Delete)
 - Search Products
 - Category Filters
 - Farmer Product Management
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from database import db
from models import Farmer, Product

product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/api/products"
)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

VALID_STOCK_STATUS = (
    "In Stock",
    "Low Stock",
    "Out of Stock",
)

VALID_UNITS = (
    "kg",
    "gram",
    "quintal",
    "ton",
    "dozen",
    "piece",
    "litre",
)


def serialize_product(product):
    """
    Convert Product object into JSON.
    """

    return {
        "product_id": product.product_id,
        "farmer_id": product.farmer_id,
        "product_name": product.product_name,
        "product_category": product.product_category,
        "description": product.description,
        "harvest_date": product.harvest_date.isoformat() if product.harvest_date else None,
        "expiry_date": product.expiry_date.isoformat() if product.expiry_date else None,
        "available_quantity": product.available_quantity,
        "unit": product.unit,
        "base_price": product.base_price,
        "minimum_price": product.minimum_price,
        "product_image": product.product_image,
        "delivery_available": product.delivery_available,
        "pickup_available": product.pickup_available,
        "stock_status": product.stock_status,
        "organic_certified": product.organic_certified,
        "active_status": product.active_status,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def get_logged_in_farmer():
    """
    Return currently logged-in farmer.
    """

    claims = get_jwt()

    if claims.get("user_type") != "farmer":
        return None

    farmer_id = int(get_jwt_identity())

    return Farmer.query.get(farmer_id)


# ---------------------------------------------------------
# Add Product
# ---------------------------------------------------------

@product_bp.route("/", methods=["POST"])
@jwt_required()
def add_product():

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can add products."
        }), 403

    data = request.get_json(silent=True) or {}

    required_fields = [
        "product_name",
        "available_quantity",
        "base_price"
    ]

    missing = [
        field
        for field in required_fields
        if not str(data.get(field, "")).strip()
    ]

    if missing:
        return jsonify({
            "success": False,
            "message": f"Missing fields: {', '.join(missing)}"
        }), 400

    try:
        quantity = float(data["available_quantity"])
        price = float(data["base_price"])
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Quantity and Base Price must be valid numbers."
        }), 400

    if quantity < 0:
        return jsonify({
            "success": False,
            "message": "Quantity cannot be negative."
        }), 400

    if price <= 0:
        return jsonify({
            "success": False,
            "message": "Base price must be greater than zero."
        }), 400

    minimum_price = data.get("minimum_price")

    if minimum_price is not None:

        try:
            minimum_price = float(minimum_price)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Minimum price must be a valid number."
            }), 400

        if minimum_price <= 0:
            return jsonify({
                "success": False,
                "message": "Minimum price must be greater than zero."
            }), 400

        if minimum_price > price:
            return jsonify({
                "success": False,
                "message": "Minimum price cannot exceed base price."
            }), 400

    unit = data.get("unit", "kg")

    if unit not in VALID_UNITS:
        return jsonify({
            "success": False,
            "message": "Invalid unit."
        }), 400

    stock_status = data.get("stock_status", "In Stock")

    if stock_status not in VALID_STOCK_STATUS:
        return jsonify({
            "success": False,
            "message": "Invalid stock status."
        }), 400

    harvest_date = None
    expiry_date = None

    if data.get("harvest_date"):
        try:
            harvest_date = datetime.strptime(
                data["harvest_date"],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid harvest date format. Use YYYY-MM-DD."
            }), 400

    if data.get("expiry_date"):
        try:
            expiry_date = datetime.strptime(
                data["expiry_date"],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid expiry date format. Use YYYY-MM-DD."
            }), 400

    product = Product(
        farmer_id=farmer.farmer_id,
        product_name=data["product_name"].strip(),
        product_category=data.get("product_category"),
        description=data.get("description"),
        harvest_date=harvest_date,
        expiry_date=expiry_date,
        available_quantity=quantity,
        unit=unit,
        base_price=price,
        minimum_price=minimum_price,
        product_image=data.get("product_image"),
        delivery_available=data.get("delivery_available", False),
        pickup_available=data.get("pickup_available", True),
        stock_status=stock_status,
        organic_certified=data.get("organic_certified", False),
    )

    db.session.add(product)

    farmer.total_products += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product added successfully.",
        "product": serialize_product(product)
    }), 201


# ---------------------------------------------------------
# Get All Active Products
# ---------------------------------------------------------

@product_bp.route("/", methods=["GET"])
def get_all_products():
    """
    Return all active products.
    """

    products = (
        Product.query
        .filter_by(active_status=True)
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Get Product By ID
# ---------------------------------------------------------

@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Return a single product.
    """

    product = Product.query.filter_by(
        product_id=product_id,
        active_status=True
    ).first()

    if product is None:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    return jsonify({
        "success": True,
        "product": serialize_product(product)
    }), 200


# ---------------------------------------------------------
# Get Logged-in Farmer Products
# ---------------------------------------------------------

@product_bp.route("/my-products", methods=["GET"])
@jwt_required()
def get_my_products():
    """
    Return all products created by the logged-in farmer.
    """

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can view their products."
        }), 403

    products = (
        Product.query
        .filter_by(
            farmer_id=farmer.farmer_id,
            active_status=True
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Get Products By Farmer ID
# ---------------------------------------------------------

@product_bp.route("/farmer/<int:farmer_id>", methods=["GET"])
def get_farmer_products(farmer_id):
    """
    Return all active products of a farmer.
    """

    farmer = Farmer.query.filter_by(
        farmer_id=farmer_id,
        active_status=True
    ).first()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Farmer not found."
        }), 404

    products = (
        Product.query
        .filter_by(
            farmer_id=farmer_id,
            active_status=True
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "farmer_id": farmer_id,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Update Product
# ---------------------------------------------------------

@product_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    """
    Update an existing product.
    Only the farmer who created the product can update it.
    """

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can update products."
        }), 403

    product = Product.query.filter_by(
        product_id=product_id,
        active_status=True
    ).first()

    if product is None:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    if product.farmer_id != farmer.farmer_id:
        return jsonify({
            "success": False,
            "message": "You are not authorized to update this product."
        }), 403

    data = request.get_json(silent=True) or {}

    # -----------------------------------------------------
    # Update Product Name
    # -----------------------------------------------------
    if "product_name" in data:
        if not str(data["product_name"]).strip():
            return jsonify({
                "success": False,
                "message": "Product name cannot be empty."
            }), 400

        product.product_name = data["product_name"].strip()

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------
    if "product_category" in data:
        product.product_category = data["product_category"]

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------
    if "description" in data:
        product.description = data["description"]

    # -----------------------------------------------------
    # Quantity
    # -----------------------------------------------------
    if "available_quantity" in data:

        try:
            quantity = float(data["available_quantity"])
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid quantity."
            }), 400

        if quantity < 0:
            return jsonify({
                "success": False,
                "message": "Quantity cannot be negative."
            }), 400

        product.available_quantity = quantity

    # -----------------------------------------------------
    # Unit
    # -----------------------------------------------------
    if "unit" in data:

        if data["unit"] not in VALID_UNITS:
            return jsonify({
                "success": False,
                "message": "Invalid unit."
            }), 400

        product.unit = data["unit"]

    # -----------------------------------------------------
    # Base Price
    # -----------------------------------------------------
    if "base_price" in data:

        try:
            price = float(data["base_price"])
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid base price."
            }), 400

        if price <= 0:
            return jsonify({
                "success": False,
                "message": "Base price must be greater than zero."
            }), 400

        product.base_price = price

    # -----------------------------------------------------
    # Minimum Price
    # -----------------------------------------------------
    if "minimum_price" in data:

        try:
            minimum = float(data["minimum_price"])
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid minimum price."
            }), 400

        if minimum <= 0:
            return jsonify({
                "success": False,
                "message": "Minimum price must be greater than zero."
            }), 400

        if minimum > product.base_price:
            return jsonify({
                "success": False,
                "message": "Minimum price cannot exceed base price."
            }), 400

        product.minimum_price = minimum

    # -----------------------------------------------------
    # Harvest Date
    # -----------------------------------------------------
    if "harvest_date" in data and data["harvest_date"]:

        product.harvest_date = datetime.strptime(
            data["harvest_date"],
            "%Y-%m-%d"
        ).date()

    # -----------------------------------------------------
    # Expiry Date
    # -----------------------------------------------------
    if "expiry_date" in data and data["expiry_date"]:

        product.expiry_date = datetime.strptime(
            data["expiry_date"],
            "%Y-%m-%d"
        ).date()

    # -----------------------------------------------------
    # Product Image
    # -----------------------------------------------------
    if "product_image" in data:
        product.product_image = data["product_image"]

    # -----------------------------------------------------
    # Delivery Options
    # -----------------------------------------------------
    if "delivery_available" in data:
        product.delivery_available = bool(data["delivery_available"])

    if "pickup_available" in data:
        product.pickup_available = bool(data["pickup_available"])

    # -----------------------------------------------------
    # Organic Certification
    # -----------------------------------------------------
    if "organic_certified" in data:
        product.organic_certified = bool(data["organic_certified"])

    # -----------------------------------------------------
    # Stock Status
    # -----------------------------------------------------
    if "stock_status" in data:

        if data["stock_status"] not in VALID_STOCK_STATUS:
            return jsonify({
                "success": False,
                "message": "Invalid stock status."
            }), 400

        product.stock_status = data["stock_status"]

    product.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product updated successfully.",
        "product": serialize_product(product)
    }), 200


# ---------------------------------------------------------
# Soft Delete Product
# ---------------------------------------------------------

@product_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    """
    Soft delete a product.
    Only the owner farmer can delete it.
    """

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can delete products."
        }), 403

    product = Product.query.filter_by(
        product_id=product_id,
        active_status=True
    ).first()

    if product is None:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    if product.farmer_id != farmer.farmer_id:
        return jsonify({
            "success": False,
            "message": "You are not authorized to delete this product."
        }), 403

    product.active_status = False
    product.updated_at = datetime.utcnow()

    if farmer.total_products > 0:
        farmer.total_products -= 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product deleted successfully."
    }), 200


# ---------------------------------------------------------
# Search Products
# ---------------------------------------------------------

@product_bp.route("/search", methods=["GET"])
def search_products():
    """
    Search products by product name.
    Example:
        /api/products/search?name=tomato
    """

    keyword = request.args.get("name", "").strip()

    if not keyword:
        return jsonify({
            "success": False,
            "message": "Search keyword is required."
        }), 400

    products = (
        Product.query
        .filter(
            Product.active_status == True,
            Product.product_name.ilike(f"%{keyword}%")
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Filter By Category
# ---------------------------------------------------------

@product_bp.route("/category/<string:category>", methods=["GET"])
def get_products_by_category(category):
    """
    Get all products belonging to a category.
    """

    products = (
        Product.query
        .filter(
            Product.active_status == True,
            Product.product_category.ilike(category)
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "category": category,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Filter By District
# ---------------------------------------------------------

@product_bp.route("/district/<string:district>", methods=["GET"])
def get_products_by_district(district):
    """
    Return all active products available
    in the specified district.
    """

    products = (
        Product.query
        .join(Farmer)
        .filter(
            Farmer.district.ilike(district),
            Farmer.active_status == True,
            Product.active_status == True
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "district": district,
        "count": len(products),
        "products": [
            serialize_product(product)
            for product in products
        ]
    }), 200


# ---------------------------------------------------------
# Update Product Stock
# ---------------------------------------------------------

@product_bp.route("/<int:product_id>/stock", methods=["PATCH"])
@jwt_required()
def update_product_stock(product_id):
    """
    Update only the product quantity and automatically
    determine the stock status.
    """

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can update stock."
        }), 403

    product = Product.query.filter_by(
        product_id=product_id,
        active_status=True
    ).first()

    if product is None:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    if product.farmer_id != farmer.farmer_id:
        return jsonify({
            "success": False,
            "message": "You are not authorized to update this product."
        }), 403

    data = request.get_json(silent=True) or {}

    if "available_quantity" not in data:
        return jsonify({
            "success": False,
            "message": "available_quantity is required."
        }), 400

    try:
        quantity = float(data["available_quantity"])
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid quantity."
        }), 400

    if quantity < 0:
        return jsonify({
            "success": False,
            "message": "Quantity cannot be negative."
        }), 400

    product.available_quantity = quantity

    # Automatically update stock status
    if quantity == 0:
        product.stock_status = "Out of Stock"
    elif quantity <= 10:
        product.stock_status = "Low Stock"
    else:
        product.stock_status = "In Stock"

    product.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock updated successfully.",
        "product": serialize_product(product)
    }), 200


# ---------------------------------------------------------
# Product Statistics (Farmer Dashboard)
# ---------------------------------------------------------

@product_bp.route("/my-products/statistics", methods=["GET"])
@jwt_required()
def product_statistics():
    """
    Returns product statistics for the logged-in farmer.
    """

    farmer = get_logged_in_farmer()

    if farmer is None:
        return jsonify({
            "success": False,
            "message": "Only farmers can access statistics."
        }), 403

    total_products = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True
    ).count()

    in_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="In Stock"
    ).count()

    low_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="Low Stock"
    ).count()

    out_of_stock = Product.query.filter_by(
        farmer_id=farmer.farmer_id,
        active_status=True,
        stock_status="Out of Stock"
    ).count()

    return jsonify({
        "success": True,
        "statistics": {
            "total_products": total_products,
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        }
    }), 200