import json
import os
import asyncio
from typing import Optional
from threading import Lock
from flask import session
from datetime import datetime, timezone

# region ===================================================== JSON SERVICE (Centralized Data Access Layer) =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

_file_locks = {}


def _get_lock(filename):
    if filename not in _file_locks:
        _file_locks[filename] = Lock()
    return _file_locks[filename]


def _get_file_path(filename):
    return os.path.join(DATA_DIR, filename)


# endregion ===================================================== JSON SERVICE (Centralized Data Access Layer) =====================================================

# region ===================================================== CORE LOAD / SAVE FUNCTIONS =====================================================
def _load_json_sync(filename):
    path = _get_file_path(filename)
    if not os.path.exists(path):
        return []

    with _get_lock(filename):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def _save_json_sync(filename, data):
    path = _get_file_path(filename)

    with _get_lock(filename):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


async def load_json(filename):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_json_sync, filename)


async def save_json(filename, data):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _save_json_sync, filename, data)


# endregion ===================================================== CORE LOAD / SAVE FUNCTIONS =====================================================

# region ===================================================== Common =====================================================
def parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        # If datetime but naive → make it UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    # Parse string
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

    # If still naive → force UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt

def get_session_user():
    return session.get("user_info")

def get_session_value(key, default=None):
    return session.get("user_info", {}).get(key, default)

def set_session_user(user, role=None, rememberMe=False):
    session["user_info"] = {
        "userId": user.get("userId"),
        "username": user.get("username"),
        "name": user.get("name"),
        "email": user.get("email"),
        "roleId": user.get("roleId"),
        "role": role.get("rolename") if role else None
    }

    session.permanent = bool(rememberMe)

def clear_session_user():
    session.clear()

# endregion ===================================================== Common =====================================================

# region ===================================================== Get =====================================================
async def load_users():
    return await load_json("users.json")


async def load_roles():
    return await load_json("roles.json")


async def load_master():
    return await load_json("master.json")


async def load_tasks():
    return await load_json("tasks.json")


async def load_daily_tasks():
    return await load_json("daily_tasks.json")


async def load_assignments():
    return await load_json("assignments.json")


async def load_approvals():
    return await load_json("approvals.json")


async def load_activity_log():
    return await load_json("activity_log.json")


async def load_archive_tasks():
    return await load_json("archive_tasks.json")


async def load_archive_assignments():
    return await load_json("archive_assignments.json")


async def load_archive_approvals():
    return await load_json("archive_approvals.json")


async def load_user_points():
    return await load_json("user_points.json")


async def load_points():
    return await load_json("points.json")


# endregion ===================================================== Get =====================================================

# region ===================================================== Get By ID =====================================================
async def get_user_by_key(itemValue, key="userId"):
    users = await load_users()
    return next((i for i in users if i.get(key) == itemValue), None)

async def get_name_by_userid(userId):
    users = await load_users() or []
    user = next((u for u in users if u.get("userId") == userId), None)
    return user.get("name") if user else None


async def get_role_by_key(itemValue, key="roleId"):
    roles = await load_roles()
    return next((i for i in roles if i.get(key) == itemValue), None)


async def get_master_label_by_code(code):
    if not code:
        return None

    MASTER_DATA = await load_master()
    
    for items in MASTER_DATA.values():
        item = next((i for i in items if i.get("code") == code), None)
        if item:
            return item.get("label")

    return None


async def get_tasks_by_key(itemValue, key="taskId"):
    tasks = await load_tasks()
    return next((i for i in tasks if i.get(key) == itemValue), None)


async def get_daily_tasks_by_key(itemValue, key="dailyTaskId"):
    daily_tasks = await load_daily_tasks()
    return next((i for i in daily_tasks if i.get(key) == itemValue), None)


async def get_assignments_by_key(itemValue, key="taskAssignId"):
    assignments = await load_assignments()
    return next((i for i in assignments if i.get(key) == itemValue), None)


async def get_approvals_by_key(itemValue, key="approvalId"):
    approvals = await load_approvals()
    return next((i for i in approvals if i.get(key) == itemValue), None)


async def get_activity_log_by_key(itemValue, key="logId"):
    activity_log = await load_activity_log()
    return next((i for i in activity_log if i.get(key) == itemValue), None)


async def get_archive_tasks_by_key(itemValue, key="taskId"):
    archive_tasks = await load_archive_tasks()
    return next((i for i in archive_tasks if i.get(key) == itemValue), None)


async def get_archive_assignments_by_key(itemValue, key="taskAssignId"):
    archive_assignments = await load_archive_assignments()
    return next((i for i in archive_assignments if i.get(key) == itemValue), None)


async def get_archive_approvals_by_key(itemValue, key="approvalId"):
    archive_approvals = await load_archive_approvals()
    return next((i for i in archive_approvals if i.get(key) == itemValue), None)


async def get_user_points_by_key(itemValue, key="userId"):
    user_points = await load_user_points()
    return [a for a in user_points if a.get(key) == itemValue]

async def get_points_by_key(pointType, pointAction):
    points = await load_points()
    return next((i for i in points if i.get("pointType") == pointType and i.get("pointAction") == pointAction), None)

# endregion ===================================================== Get By ID =====================================================

# region ===================================================== Save =====================================================
async def save_user(data):
    await save_json("users.json", data)

async def save_role(data):
    await save_json("roles.json", data)

async def save_master(data):
    await save_json("master.json", data)

async def save_tasks(data):
    await save_json("tasks.json", data)

async def save_daily_tasks(data):
    await save_json("daily_tasks.json", data)

async def save_assignments_tasks(data):
    await save_json("assignments.json", data)

async def save_approvals(data):
    await save_json("approvals.json", data)

async def save_activity_log(data):
    await save_json("activity_log.json", data)

async def save_archive_approvals(data):
    await save_json("archive_approvals.json", data)

async def save_archive_assignments(data):
    await save_json("archive_assignments.json", data)

async def save_archive_tasks(data):
    await save_json("archive_tasks.json", data)

async def save_user_points(data):
    await save_json("user_points.json", data)

async def save_points(data):
    await save_json("points.json", data)
# endregion ===================================================== Save =====================================================
