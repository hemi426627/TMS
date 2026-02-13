from asyncio.windows_events import NULL
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import success, error
import asyncio

async def login_async(username, password, rememberMe):
    try:
        user = None

        # 1️ Try login by username
        user = await js.get_user_by_key(username.upper(), "username")

        # 2️ If not found, try login by email
        if not user:
            user = await js.get_user_by_key(username, "email")

        if not user:
            return error("Invalid username or email", 401)

        # 3️ Password check
        if user.get("password") != password:
            return error("Invalid username/email or password", 401)

        # 4️ Role lookup
        role = await js.get_role_by_key(user.get("roleId"))

        # 5️ Store session
        js.set_session_user(user, role, rememberMe)

        return success(data=js.get_session_user(), message="Login successfully!")
    except Exception as e:
        return error(str(e), 500)

async def reset_password_async(username, oldPassword, newPassword):
    try:
        user = None

        # 1️ Try login by username
        user = await js.get_user_by_key(username.upper(), "username")

        # 2️ If not found, try login by email
        if not user:
            user = await js.get_user_by_key(username, "email")

        if not user:
            return error("Invalid username or email", 401)

        # 3️ Password check
        if user.get("password") != oldPassword:
            return error("Invalid Old Password", 401)

        await add_edit_user_async({"password":newPassword},user.get("userId"))
                
        return success(message="Password updated successfully!")
    except Exception as e:
        return error(str(e), 500)

async def get_users_async():
    try:
        users = await js.load_users()
        roles = await js.load_roles()

        role_map = {r.get("roleId"): r.get("rolename", "Unknown") for r in roles}

        # Replace roleId with role name
        for user in users:
            role_id = user.get("roleId")
            user["role"] = role_map.get(role_id, "Unknown")
            user.pop("roleId", None)

        return success(users)
    except Exception as e:
        return error(str(e), 500)

async def get_user_by_id_async(user_id):
    try:
        user = await js.get_user_by_key(user_id)
        if not user:
            return error("User not found", 404)
        return success(user)
    except Exception as e:
        return error(str(e), 500)

async def add_edit_user_async(user_data, user_id=None):
    try:
        users = await js.load_users()
        roles = await js.load_roles()

        if user_id is not None and user_id > 0:
            index = next((i for i, u in enumerate(users) if u["userId"] == user_id), None)
            if index is None:
                return error("User not found", 404)

            # Update only the passed fields
            users[index].update(user_data)

            await js.save_json("users.json", users)
            return success(data=users[index], message="User Updated Successfully!")
        else:
            # ---------------- ADD ----------------
            if users:
                max_id = max(u["userId"] for u in users)
                new_user_id = max_id + 1
            else:
                new_user_id = 1  # start from 1 if no users exist

            user_data["userId"] = new_user_id

            if any(u["userId"] == new_user_id for u in users):
                return error("User with this ID already exists", 400)

            active = "true"
            user_data["active"] = active

            users.append(user_data)
            await js.save_json("users.json", users)
            return success(data=user_data, message="User Added Successfully!")
    except Exception as e:
        return error(str(e), 500)

async def remove_user_by_id_async(user_id):
    try:
        users = await js.load_users()

        # Find the user to delete
        user_to_delete = next((u for u in users if u["userId"] == user_id), None)
        if not user_to_delete:
            return error("User not found", 404)

        # Filter out the user
        new_users = [u for u in users if u["userId"] != user_id]
        await js.save_json("users.json", new_users)

        user_name = user_to_delete.get("name", str(user_id))
        return success(data=new_users, message=f"User '{user_name}' removed successfully")
    except Exception as e:
        return error(str(e), 500)