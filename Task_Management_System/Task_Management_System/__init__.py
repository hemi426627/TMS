from flask import Flask  # type: ignore

app = Flask(__name__)

from Task_Management_System import views

from Task_Management_System.blueprints.api import api

app.register_blueprint(api)