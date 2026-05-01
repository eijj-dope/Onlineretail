from flask import Blueprint, render_template, request, redirect, session
import config

user_routes = Blueprint("user_routes", __name__)

# Login
@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/home")

    # GET request
    if request.method == "GET":
        return render_template("login.html")

    # POST request
    email = request.form["email"].strip()
    password = request.form["password"].strip()

    conn = config.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        # Check password manually
        if user["password"] == password:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/home")

        else:
            return "Wrong password. <a href='/login'>Try again</a>"

    return "User not found. <a href='/login'>Try again</a>"


# Register
@user_routes.route("/register", methods=["GET","POST"])
def register():
    if "user_id" in session:
        return redirect("/home")
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = config.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@user_routes.route("/my_orders")
def my_orders():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = config.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT order_id, total, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_orders.html", orders=orders)

@user_routes.route("/cancel_order/<int:order_id>")
def cancel_order(order_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = config.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Check ownership
    cursor.execute("""
        SELECT status FROM orders
        WHERE order_id=%s AND user_id=%s
    """, (order_id, user_id))

    order = cursor.fetchone()

    if not order:
        return "Order not found"

    # 🚫 Restriction
    if order["status"] in ["Shipped", "Completed"]:
        return "Cannot cancel this order"

    # ✅ Restore stock
    cursor.execute("""
        SELECT product_id, quantity
        FROM order_items
        WHERE order_id=%s
    """, (order_id,))
    items = cursor.fetchall()

    for item in items:
        cursor.execute("""
            UPDATE products
            SET stock = stock + %s
            WHERE product_id = %s
        """, (item["quantity"], item["product_id"]))

    # ✅ Update status
    cursor.execute("""
        UPDATE orders
        SET status='Cancelled'
        WHERE order_id=%s
    """, (order_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/my_orders")

# Logout
@user_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")