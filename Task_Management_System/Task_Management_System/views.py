from flask import render_template, jsonify  # type: ignore
from Task_Management_System import app
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import *


# ================= HOME ==================
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", title="Home")


# ================= ABOUT ==================
@app.route("/about")
def about():
    return render_template("about.html", title="About")


# ================= CONTACT ==================
@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")