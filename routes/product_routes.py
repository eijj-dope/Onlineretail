from flask import Blueprint, render_template, request, session, jsonify
import mysql.connector
import config

product_routes = Blueprint("product_routes", __name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host=config.DB_CONFIG["host"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"]
    )
    return conn


# Show products
@product_routes.route("/products")
def show_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("product.html", products=products_list)

# Add to cart
@product_routes.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")

    # initialize session cart if not exists
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    # Increase quantity if already in cart
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart  # save back to session
    return jsonify({"message": "Product added to cart!"})

# View cart
@product_routes.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    products_in_cart = []

    if cart:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get product info for all product_ids in cart
        format_strings = ','.join(['%s'] * len(cart))
        cursor.execute(f"SELECT * FROM products WHERE product_id IN ({format_strings})", tuple(cart.keys()))
        products_in_cart = cursor.fetchall()
        cursor.close()
        conn.close()

        # Add quantity from session cart
        for product in products_in_cart:
            product["quantity"] = cart[str(product["product_id"])]
            product["total"] = product["price"] * product["quantity"]

    total_price = sum(p["total"] for p in products_in_cart) if products_in_cart else 0

    return render_template("cart.html", cart_items=products_in_cart, total_price=total_price)