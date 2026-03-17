from flask import Flask, render_template, session, redirect
import config
from routes.product_routes import product_routes
from routes.cart_routes import cart_routes
from routes.user_routes import user_routes

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Register blueprints
app.register_blueprint(product_routes)
app.register_blueprint(cart_routes)
app.register_blueprint(user_routes)

# Landing page: prompt login/register
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/home")
    return render_template("index.html")

# Home page after login
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")
    return render_template("home.html")

# Optional: 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)