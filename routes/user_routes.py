from flask import Blueprint, render_template, session
import mysql.connector
import config

user_routes = Blueprint("user_routes", __name__)

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host=config.DB_CONFIG["host"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"]
    )
    return conn

# Show user info (example)
@user_routes.route("/user")
def user_info():
    # For now just demo with session info or static
    user = session.get("user", {"name": "Guest"})
    return render_template("user.html", user=user)