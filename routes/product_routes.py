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
    product_id = data.get("product_id")
    user_id = session["user_id"]

    if not product_id:
        return jsonify({"message": "No product selected!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (%s,%s,1)
            ON DUPLICATE KEY UPDATE quantity = quantity + 1
        """, (user_id, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Product added to cart!"})
    except Exception as e:
        print("Add to cart error:", e)
        return jsonify({"message": "Error adding product to cart"}), 500