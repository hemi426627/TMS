from flask import Blueprint, request, jsonify  # type: ignore
from Task_Management_System.services.task_service import *
from Task_Management_System.services.user_service import *
from Task_Management_System.services.roles_service import *
from Task_Management_System.services.master_service import *
from Task_Management_System.services.dashboard_service import *

api = Blueprint("api", __name__, url_prefix="/api")

# region --------------------------- Dashboard ---------------------------
@api.route("/get_user_main_tasks", methods=["GET"])
async def get_user_main_tasks():
    return await get_user_main_tasks_async()

@api.route("/get_user_daily_tasks", methods=["GET"])
async def get_user_daily_tasks():
    return await get_user_daily_tasks_async()

@api.route("/update_main_task_status", methods=["POST"])
async def update_main_task_status():
    request_data = request.json
    return await update_main_task_status_async(request_data)
# endregion --------------------------- Dashboard ---------------------------

# region --------------------------- TASKS ---------------------------
@api.route("/get_all_tasks", methods=["GET"])
async def get_all_tasks():
    showArchive = request.args.get("showArchive", "false").lower() == "true"
    return await get_all_tasks_async(showArchive=showArchive)

@api.route("/get_main_tasks", methods=["GET"])
async def get_main_tasks():
    showArchive = request.args.get("showArchive", "false").lower() == "true"
    return await get_main_tasks_async(showArchive=showArchive)

@api.route("/get_sub_tasks_by_TaskId", methods=["GET"])
async def get_sub_tasks_by_TaskId():
    taskId = request.args.get("taskId", type=int)
    showArchive = request.args.get("showArchive", "false").lower() == "true"
    return await get_sub_tasks_by_TaskId_async(taskId=taskId, showArchive=showArchive)

@api.route("/get_task_by_TaskId", methods=["GET"])
async def get_task_by_TaskId():
    taskId = request.args.get("taskId", type=int)
    return await get_task_by_TaskId_async(taskId=taskId)

@api.route("/get_assignment_by_TaskId", methods=["GET"])
async def get_assignment_by_TaskId():
    taskId = request.args.get("taskId", type=int)
    return await get_assignment_by_TaskId_async(taskId=taskId)

@api.route("/get_assignment_by_TaskId_AssignTo", methods=["GET"])
async def get_assignment_by_TaskId_AssignTo():
    taskId = request.args.get("taskId", type=int)
    assignTo = request.args.get("assignTo", type=int)
    return await get_assignment_by_TaskId_AssignTo_async(taskId=taskId,assignTo=assignTo)

@api.route("/add_edit_assignments", methods=["POST"])
async def add_edit_assignments():
    data = request.get_json()
    return await add_edit_assignments_async(data)

@api.route("/add_edit_task", methods=["POST"])
async def add_edit_task():
    task_id = request.args.get("task_id", type=int)
    data = request.json
    return await add_edit_task_async(data, task_id=task_id)

@api.route("/remove_task_by_Id/<int:task_id>", methods=["POST"])
async def remove_task_by_Id(task_id):
    return await remove_task_by_id_async(task_id)

@api.route("/get_admin_panel_dropdown", methods=["GET"])
async def get_admin_panel_dropdown():
    return await get_admin_panel_dropdown_async()

@api.route("/archive_restore_task", methods=["POST"])
async def archive_restore_task():
    data = request.args
    taskId = data.get("taskId", type=int)
    isSubTask = data.get("isSubTask", "false").lower() == "true"
    restoreTask = data.get("restoreTask", "false").lower() == "true"
    return await archive_restore_task_async(
        taskId=taskId,
        isSubTask=isSubTask,
        restoreTask=restoreTask
    )
# endregion --------------------------- TASKS ---------------------------

# region --------------------------- USERS ---------------------------
@api.route("/login", methods=["POST"])
async def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    rememberMe = data.get("rememberMe")
    return await login_async(username, password, rememberMe)

@api.route("/reset_password", methods=["POST"])
async def reset_password():
    data = request.json
    username = data.get("username")
    oldPassword = data.get("oldPassword")
    newPassword = data.get("newPassword")
    return await reset_password_async(username, oldPassword, newPassword)

@api.route("/get_users", methods=["GET"])
async def get_users():
    return await get_users_async()

@api.route("/get_user_by_Id/<int:user_id>", methods=["GET"])
async def get_user_by_Id(user_id):
    return await get_user_by_id_async(user_id)


@api.route("/add_edit_user", methods=["POST"])
async def add_edit_user():
    user_id = request.args.get("user_id", type=int)
    data = request.json
    return await add_edit_user_async(data, user_id=user_id)


@api.route("/remove_user_by_Id/<int:user_id>", methods=["POST"])
async def remove_user_by_Id(user_id):
    return await remove_user_by_id_async(user_id)

# endregion --------------------------- USERS ---------------------------

# region --------------------------- ROLES ---------------------------
@api.route("/get_roles", methods=["GET"])
async def get_roles():
    return await get_roles_async()

@api.route("/get_role_by_Id/<int:role_id>", methods=["GET"])
async def get_role_by_Id(role_id):
    return await get_role_by_id_async(role_id)


@api.route("/add_edit_role", methods=["POST"])
async def add_edit_role():
    role_id = request.args.get("role_id", type=int)
    data = request.json
    return await add_edit_role_async(data, role_id=role_id)


@api.route("/remove_role_by_Id/<int:role_id>", methods=["POST"])
async def remove_role_by_Id(role_id):
    return await remove_role_by_id_async(role_id)
# endregion --------------------------- ROLES ---------------------------

# region --------------------------- MASTERS ---------------------------
@api.route("/get_master_categories", methods=["GET"])
async def get_master_categories():
    return await load_master_categories_async()


@api.route("/get_master_category/<string:category>", methods=["GET"])
async def get_master_category(category):
    return await get_master_category_list_async(category)

@api.route("/get_master_item/<string:category>/<string:code>", methods=["GET"])
async def get_master_item(category, code):
    return await get_master_item_async(category, code)


@api.route("/add_edit_master", methods=["POST"])
async def add_edit_master():
    category = request.args.get("masterCategory", "")
    code = request.args.get("masterCode", "")
    data = request.json
    return await add_edit_master_async(category, code, data)


@api.route("/remove_master_by_code/<string:category>/<string:code>", methods=["POST"])
async def remove_master(category, code):
    return await remove_master_by_code_async(category, code)
# endregion --------------------------- MASTERS ---------------------------
