import json
import os
from threading import Lock

# =====================================================
# JSON SERVICE (Centralized Data Access Layer)
# =====================================================

# _BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

_file_locks = {}


def _get_lock(filename):
    if filename not in _file_locks:
        _file_locks[filename] = Lock()
    return _file_locks[filename]


def _get_file_path(filename):
    return os.path.join(DATA_DIR, filename)


# =====================================================
# CORE LOAD / SAVE FUNCTIONS
# =====================================================


def load_json(filename):
    path = _get_file_path(filename)
    if not os.path.exists(path):
        return []
    with _get_lock(filename):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def save_json(filename, data):
    path = _get_file_path(filename)
    with _get_lock(filename):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# =====================================================
# USERS
# =====================================================


def get_users():
    return load_json("users.json")


def get_user_by_id(user_id):
    return next((u for u in get_users() if u["userId"] == user_id), None)


# =====================================================
# ROLES / LOOKUPS
# =====================================================


def get_roles():
    return load_json("roles.json")


def get_master():
    return load_json("master.json")


# =====================================================
# TASKS
# =====================================================


def get_tasks():
    return load_json("tasks.json")


def get_task_by_id(task_id):
    return next((t for t in get_tasks() if t["taskId"] == task_id), None)


# =====================================================
# ASSIGNMENTS
# =====================================================


def get_assignments():
    return load_json("assignments.json")


def get_assignments_by_task(task_id):
    return [a for a in get_assignments() if a["taskId"] == task_id]


def get_assignments_by_user(user_id):
    return [a for a in get_assignments() if a["assignedTo"] == user_id]


# =====================================================
# APPROVALS
# =====================================================


def get_approvals():
    return load_json("approvals.json")


def get_approvals_by_task(task_id):
    return [a for a in get_approvals() if a["taskId"] == task_id]


# =====================================================
# DAILY TASKS
# =====================================================


def get_daily_tasks():
    return load_json("daily_tasks.json")


def get_daily_tasks_by_user(user_id):
    return [d for d in get_daily_tasks() if d["userId"] == user_id]


# =====================================================
# ACTIVITY LOG
# =====================================================


def get_activity_logs():
    return load_json("activity_log.json")


def get_logs_for_entity(entity_type, entity_id):
    return [
        l
        for l in get_activity_logs()
        if l["entityType"] == entity_type and l["entityId"] == entity_id
    ]


# =====================================================
# ARCHIVE HELPERS
# =====================================================


def get_archive_tasks():
    return load_json("archive_tasks.json")


def get_archive_assignments():
    return load_json("archive_assignments.json")


def get_archive_approvals():
    return load_json("archive_approvals.json")
