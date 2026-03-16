from flask import Flask, render_template, session
import config  # your existing config.py

# Import your blueprints
from routes.product_routes import product_routes
from routes.cart_routes import cart_routes
from routes.user_routes import user_routes

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # use your config SECRET_KEY

# Register blueprints
app.register_blueprint(product_routes)
app.register_blueprint(cart_routes)
app.register_blueprint(user_routes)

# Home route
@app.route("/")
def home():
    # Optional: Pass number of items in cart for display
    cart_count = sum(session.get("cart", {}).values()) if "cart" in session else 0
    return render_template("index.html", cart_count=cart_count)

# Optional: catch-all 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)