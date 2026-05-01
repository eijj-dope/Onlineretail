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

@cart_routes.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    selected_items = request.form.getlist("selected_items")

    if not selected_items:
        return "No items selected!"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cart_items = []
    total_price = 0

    for product_id in selected_items:
        # get item info
        cursor.execute("""
            SELECT p.product_id, p.name, p.price, c.quantity
            FROM cart_items c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id=%s AND c.product_id=%s
        """, (user_id, product_id))

        item = cursor.fetchone()

        if item:
            # ✅ get chosen quantity
            checkout_qty = int(request.form.get(f"checkout_qty_{product_id}", 1))

            # prevent over checkout
            if checkout_qty > item["quantity"]:
                checkout_qty = item["quantity"]

            item["checkout_qty"] = checkout_qty
            item["total"] = item["price"] * checkout_qty

            total_price += item["total"]
            cart_items.append(item)

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

    selected_items = request.form.getlist("selected_items")

    if not selected_items:
        return "No items selected!"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    order_items = []
    total = 0

    for product_id in selected_items:

        # get product + cart info
        cursor.execute("""
            SELECT c.quantity AS cart_qty, p.price, p.stock
            FROM cart_items c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id=%s AND c.product_id=%s
        """, (user_id, product_id))

        item = cursor.fetchone()

        if not item:
            continue

        # ✅ get selected quantity
        checkout_qty = int(request.form.get(f"checkout_qty_{product_id}", 1))

        # prevent over checkout
        if checkout_qty > item["cart_qty"]:
            checkout_qty = item["cart_qty"]

        # 🚨 check stock
        if checkout_qty > item["stock"]:
            return f"Not enough stock for product {product_id}"

        # compute total
        subtotal = item["price"] * checkout_qty
        total += subtotal

        order_items.append({
            "product_id": product_id,
            "quantity": checkout_qty,
            "price": item["price"]
        })

    # ✅ create order
    cursor.execute("""
        INSERT INTO orders (user_id, fullname, address, city, zip_code, payment_method, total)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (user_id, fullname, address, city, zip_code, payment, total))

    order_id = cursor.lastrowid

    # ✅ insert order items + reduce stock
    for item in order_items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s,%s,%s,%s)
        """, (order_id, item["product_id"], item["quantity"], item["price"]))

        cursor.execute("""
            UPDATE products
            SET stock = stock - %s
            WHERE product_id = %s
        """, (item["quantity"], item["product_id"]))

        # ✅ remove only checked items from cart
        cursor.execute("""
            DELETE FROM cart_items
            WHERE user_id=%s AND product_id=%s
        """, (user_id, item["product_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/home")