from flask import Flask  # type: ignore

app = Flask(__name__)
app.secret_key = "hemi_khan_secret_key_impossible_to_break"

from Task_Management_System import views

from Task_Management_System.blueprints.api import api

app.register_blueprint(api)