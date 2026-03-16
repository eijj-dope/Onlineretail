from flask import Blueprint, render_template, session
import mysql.connector
import config

cart_routes = Blueprint("cart_routes", __name__)

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host=config.DB_CONFIG["host"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"]
    )
    return conn

# View cart
@cart_routes.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    products_in_cart = []

    if cart:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get product info for all IDs in cart
        format_strings = ','.join(['%s'] * len(cart))
        cursor.execute(f"SELECT * FROM products WHERE product_id IN ({format_strings})", tuple(cart.keys()))
        products_in_cart = cursor.fetchall()
        cursor.close()
        conn.close()

        # Add quantity and total for each product
        for product in products_in_cart:
            product_id_str = str(product["product_id"])
            product["quantity"] = cart[product_id_str]
            product["total"] = product["price"] * product["quantity"]

    total_price = sum(item["total"] for item in products_in_cart) if products_in_cart else 0
    return render_template("cart.html", cart_items=products_in_cart, total_price=total_price)