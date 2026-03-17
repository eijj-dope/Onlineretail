from flask import Blueprint, render_template, request, redirect, session
import config

user_routes = Blueprint("user_routes", __name__)

# Login
@user_routes.route("/login", methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect("/home")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = config.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            return redirect("/home")
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")


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


# Logout
@user_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")