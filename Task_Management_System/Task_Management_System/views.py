from flask import render_template, redirect, url_for  # type: ignore
from Task_Management_System import app
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import *

# ================= Helper: check login ==================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not js.get_session_user():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ================= Login ==================
@app.route("/")
def login():
     if js.get_session_user():
        return redirect(url_for("dashboard"))
     return render_template("login.html", title="Login")

 # ================= Logout ==================
@app.route("/logout")
def logout():
    js.clear_session_user()
    return redirect(url_for("login"))

# ================= Dashboard ==================
@app.route("/dashboard")
@login_required
def dashboard():
    user_info = js.get_session_user()
    return render_template("index.html", title="Dashboard", user_info=user_info)

# ================= Admin Panel ==================
@app.route("/admin")
@login_required
def admin():
    user_info = js.get_session_user()
    return render_template("admin.html", title="Admin Panel", user_info=user_info)
