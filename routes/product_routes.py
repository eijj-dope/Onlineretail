from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
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
    # must be logged in
    if "user_id" not in session:
        return redirect(url_for("user_routes.login"))

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
    if "user_id" not in session:
        return jsonify({"message": "Please login first!"}), 401

    data = request.get_json()

    try:
        product_id = int(data.get("product_id"))
    except:
        return jsonify({"message": "Invalid product"}), 400

    qty_raw = str(data.get("quantity", "")).strip()

    try:
        quantity = int(qty_raw) if qty_raw else 1
        if quantity < 1:
            quantity = 1
    except:
        quantity = 1

    user_id = session["user_id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (user_id, product_id, quantity, quantity))

        conn.commit()

        print("✅ ADDED:", user_id, product_id, quantity)  # DEBUG

        cursor.close()
        conn.close()

        return jsonify({"message": "Added to cart!"})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"message": "Database error"}), 500