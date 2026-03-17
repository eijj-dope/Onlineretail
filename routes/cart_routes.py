from flask import Blueprint, render_template, session, redirect, url_for
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
        return redirect(url_for("user_routes.login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.product_id, p.name, p.price, c.quantity, (p.price * c.quantity) AS total
        FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id=%s
    """, (user_id,))
    products_in_cart = cursor.fetchall()
    cursor.close()
    conn.close()

    total_price = sum(p["total"] for p in products_in_cart) if products_in_cart else 0

    return render_template("cart.html", cart_items=products_in_cart, total_price=total_price)