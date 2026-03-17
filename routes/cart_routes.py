from flask import Blueprint, render_template, session, redirect, url_for, request
import mysql.connector
import config

cart_routes = Blueprint("cart_routes", __name__)

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
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.product_id, p.name, p.price, c.quantity,
               (p.price * c.quantity) AS total
        FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))

    cart_items = cursor.fetchall()

    cursor.close()
    conn.close()

    total_price = sum(item["total"] for item in cart_items)

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@cart_routes.route("/checkout")
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.product_id, p.name, p.price, c.quantity,
               (p.price * c.quantity) AS total
        FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id=%s
    """, (user_id,))

    cart_items = cursor.fetchall()
    total_price = sum(item["total"] for item in cart_items)

    cursor.close()
    conn.close()

    return render_template("checkout.html", cart_items=cart_items, total_price=total_price)

@cart_routes.route("/place_order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    address = request.form.get("address")
    fullname = request.form.get("fullname")
    city = request.form.get("city")
    zip_code = request.form.get("zip")
    payment = request.form.get("payment_method")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get cart items with price
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.price, p.stock
        FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id=%s
    """, (user_id,))
    items = cursor.fetchall()

    # 🚨 Check stock first
    for item in items:
        if item["quantity"] > item["stock"]:
            return "Not enough stock for a product!"

    # Compute total
    total = sum(item["price"] * item["quantity"] for item in items)

    # ✅ Insert into orders
    cursor.execute("""
        INSERT INTO orders (user_id, fullname, address, city, zip_code, payment_method, total)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (user_id, fullname, address, city, zip_code, payment, total))

    order_id = cursor.lastrowid

    # ✅ Insert into order_items + reduce stock
    for item in items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s,%s,%s,%s)
        """, (order_id, item["product_id"], item["quantity"], item["price"]))

        cursor.execute("""
            UPDATE products
            SET stock = stock - %s
            WHERE product_id = %s
        """, (item["quantity"], item["product_id"]))

    # ✅ Clear cart
    cursor.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/home")