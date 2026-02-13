from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import success, error
import asyncio


async def load_master_categories_async():
    try:
        master_data = await js.load_master()
        if not master_data:
            return error(message="Master data not found", status_code=404)
        return success(list(master_data.keys()))
    except Exception as e:
        return error(str(e), 500)

async def get_master_category_list_async(category):
    try:
        master_data = await js.load_master()

        if not master_data:
            return error(message="Master data not found", status_code=404)

        if category not in master_data:
            return error(message="Invalid category", status_code=400)

        items = master_data.get(category, [])

        return success(items)
    except Exception as e:
        return error(str(e), 500)

async def get_master_item_async(category, code):
    try:
        master_data = await js.load_master()
        items = master_data.get(category, [])
        item = next((x for x in items if x["code"] == code), None)

        if not item:
            return error("Master item not found", 404)

        return success(item)
    except Exception as e:
        return error(str(e), 500)

async def add_edit_master_async(category, code, data):
    try:
        master_data = await js.load_master()

        if category not in master_data:
            master_data[category] = []

        items = master_data[category]

        # EDIT
        if code:
            for item in items:
                if item["code"] == code:
                    item.update(data)
                    await js.save_master(master_data)
                    return success(item, "Master Updated Successfully!")

            return error("Master item not found", 404)

        # ADD
        if any(x["code"] == data["code"] for x in items):
            return error("Code already exists", 400)

        items.append(data)
        await js.save_master(master_data)
        return success(data, "Master Added Successfully!")

    except Exception as e:
        return error(str(e), 500)

async def remove_master_by_code_async(category, code):
    try:
        master_data = await js.load_master()

        if category not in master_data:
            return error("Category not found", 404)

        items = master_data[category]
        new_items = [x for x in items if x["code"] != code]

        if len(items) == len(new_items):
            return error("Master item not found", 404)

        master_data[category] = new_items
        await js.save_master(master_data)

        return success(message="Master deleted successfully!")
    except Exception as e:
        return error(str(e), 500)