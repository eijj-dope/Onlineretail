from flask import Blueprint, render_template, session, redirect, request
import mysql.connector
import config
import os
from werkzeug.utils import secure_filename
import json

admin_routes = Blueprint("admin_routes", __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=config.DB_CONFIG["host"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"]
    )

UPLOAD_FOLDER = "static/images"

# =========================
# ADMIN DASHBOARD
# =========================
@admin_routes.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Unauthorized"

    return render_template("admin_dashboard.html")


# =========================
# VIEW ORDERS
# =========================
@admin_routes.route("/admin/orders")
def admin_orders():
    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Unauthorized", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.order_id, u.name, o.total, o.status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.created_at DESC
    """)

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_orders.html", orders=orders)

# =========================
# UPDATE ORDER STATUS
# =========================
@admin_routes.route("/admin/update_status", methods=["POST"])
def update_status():
    if "user_id" not in session or session.get("role") != "admin":
        return "Unauthorized", 403

    order_id = request.form.get("order_id")
    new_status = request.form.get("status")

    if not order_id or not new_status:
        return "Invalid input", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ GET CURRENT STATUS
    cursor.execute("SELECT status FROM orders WHERE order_id=%s", (order_id,))
    order = cursor.fetchone()

    if not order:
        return "Order not found"

    current_status = order["status"]

    # 🚫 PREVENT CANCEL IF COMPLETED
    if current_status == "Completed" and new_status == "Cancelled":
        return "Cannot cancel completed order"

    # 🚨 ONLY RESTORE IF CHANGING TO CANCELLED
    if new_status.lower() == "cancelled" and (not current_status or current_status.lower() != "cancelled"):


        # GET ORDER ITEMS
        cursor.execute("""
            SELECT product_id, quantity
            FROM order_items
            WHERE order_id=%s
        """, (order_id,))
        items = cursor.fetchall()
        
        print("ITEMS FOUND:", items)
        # ✅ RETURN STOCK
        for item in items:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])

            print("UPDATING:", product_id, quantity)

            cursor.execute("""
                UPDATE products
                SET stock = stock + %s
                WHERE product_id = %s
            """, (quantity, product_id))

            print("ROWS AFFECTED:", cursor.rowcount)

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/orders")

# =========================
# VIEW PRODUCTS
# =========================
@admin_routes.route("/admin/products")
def admin_products():
    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Unauthorized", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_products.html", products=products)

# =========================
# ADD PRODUCT
# =========================
@admin_routes.route("/admin/add_product", methods=["POST"])
def add_product():
    if "user_id" not in session or session.get("role") != "admin":
        return "Unauthorized", 403

    name = request.form.get("name")
    price = request.form.get("price")
    stock = request.form.get("stock")
    image = request.files.get("image")

    filename = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, price, stock, image)
        VALUES (%s, %s, %s, %s)
    """, (name, price, stock, filename))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/products")

# =========================
# DELETE PRODUCT
# =========================
@admin_routes.route("/admin/delete_product/<int:product_id>")
def delete_product(product_id):
    if "user_id" not in session or session.get("role") != "admin":
        return "Unauthorized", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/products")

@admin_routes.route("/admin/inventory")
def admin_inventory():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name, stock FROM products")
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_inventory.html", products=products)

@admin_routes.route("/admin/sales")
def admin_sales():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(total)
    FROM orders
    WHERE status = 'Delivered'
    """)
    total_sales = cursor.fetchone()[0] or 0

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE status = 'Delivered'
    """)
    total_orders = cursor.fetchone()[0]

    cursor.execute("""
    SELECT DATE(created_at), SUM(total)
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY DATE(created_at)
    ORDER BY DATE(created_at)
    """)
    sales_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # ✅ FIX: ensure not None
    dates = [str(row[0]) for row in sales_data] if sales_data else []
    totals = [float(row[1]) for row in sales_data] if sales_data else []

    return render_template("admin_sales.html",
        total_sales=total_sales,
        total_orders=total_orders,
        dates=json.dumps(dates),   # ✅ IMPORTANT
        totals=json.dumps(totals)  # ✅ IMPORTANT
    )

@admin_routes.route("/admin/profile")
def admin_profile():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    return render_template("admin_profile.html")

@admin_routes.route("/admin/order/<int:order_id>")
def admin_order_detail(order_id):
    if "user_id" not in session or session.get("role") != "admin":
        return "Unauthorized", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get order info
    cursor.execute("""
        SELECT o.*, u.name
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_id=%s
    """, (order_id,))
    order = cursor.fetchone()

    # Get items inside order
    cursor.execute("""
        SELECT p.name, oi.quantity, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id=%s
    """, (order_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_order_detail.html", order=order, items=items)