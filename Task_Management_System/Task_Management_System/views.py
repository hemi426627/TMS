from flask import render_template, jsonify  # type: ignore
from Task_Management_System import app
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import *


# ================= Dashboard ==================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("index.html", title="Dashboard")


# ================= Admin Panel ==================
@app.route("/admin")
def admin():
    return render_template("admin.html", title="Admin Panel")
