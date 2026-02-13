from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import success, error
import asyncio


async def get_roles_async():
    try:
        roles = await js.load_roles()
        return success(roles)
    except Exception as e:
        return error(str(e), 500)

async def get_role_by_id_async(role_id):
    try:
        role = await js.get_role_by_key(role_id)
        if not role:
            return error("Role not found", 404)
        return success(role)
    except Exception as e:
        return error(str(e), 500)

async def add_edit_role_async(role_data, role_id=None):
    try:
        roles = await js.load_roles()

        if role_id is not None and role_id > 0:
            index = next((i for i, u in enumerate(roles) if u["roleId"] == role_id), None)
            if index is None:
                return error("Role not found", 404)

            # Update only the passed fields
            roles[index].update(role_data)

            await js.save_json("roles.json", roles)
            return success(data=roles[index], message="Role Updated Successfully!")
        else:
            # ---------------- ADD ----------------
            if roles:
                max_id = max(u["roleId"] for u in roles)
                new_role_id = max_id + 1
            else:
                new_role_id = 1  # start from 1 if no users exist

            role_data["roleId"] = new_role_id

            if any(u["roleId"] == new_role_id for u in roles):
                return error("Role with this ID already exists", 400)

            roles.append(role_data)
            await js.save_json("roles.json", roles)
            return success(data=role_data, message="Role Added Successfully!")
    except Exception as e:
        return error(str(e), 500)

async def remove_role_by_id_async(role_id):
    try:
        roles = await js.load_roles()

        # Find the user to delete
        role_to_delete = next((u for u in roles if u["roleId"] == role_id), None)
        if not role_to_delete:
            return error("Role not found", 404)

        # Filter out the user
        new_roles = [u for u in roles if u["roleId"] != role_id]
        await js.save_json("roles.json", new_roles)

        rolename = role_to_delete.get("roleId", str(role_id))
        return success(data=new_roles, message=f"Role '{rolename}' removed successfully")
    except Exception as e:
        return error(str(e), 500)