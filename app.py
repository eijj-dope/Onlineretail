from flask import Flask, render_template, session, redirect
import config
from routes.product_routes import product_routes
from routes.cart_routes import cart_routes
from routes.user_routes import user_routes
from routes.admin_routes import admin_routes

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Register blueprints
app.register_blueprint(product_routes)
app.register_blueprint(cart_routes)
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)

# Landing page: prompt login/register
@app.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect("/admin/dashboard")
        return redirect("/products")
    return redirect("/login")  # Redirect to login page if not logged in

# Optional: 404
@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == "__main__":
    app.run(debug=True)