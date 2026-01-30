from flask import Blueprint, render_template  # type: ignore
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import success, error

api = Blueprint("api", __name__, url_prefix="/api")


# region --------------------------- USERS ---------------------------
@api.route("/get_users", methods=["GET"])
def get_users():
    try:
        users = js.get_users()
        return success(users)
    except Exception as e:
        return error(str(e), 500)


@api.route("/get_user_by_Id/<int:user_id>")
def get_user_by_Id(user_id):
    user = js.get_user_by_id(user_id)
    if not user:
        return error("User not found", 404)
    return success(user)


# endregion --------------------------- USERS ---------------------------
