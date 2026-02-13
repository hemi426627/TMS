from asyncio.windows_events import NULL
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import *
from datetime import datetime, timezone
import asyncio

async def get_all_tasks_async(showArchive=False):
    try:
        result = []

        tasks = await js.load_tasks()
        assignments = await js.load_assignments()
        approvals = await js.load_approvals()
        users = await js.load_users()

        # User lookup map
        user_map = {u["userId"]: u for u in users}

        archived_task_ids = set()

        if showArchive:
            archived_tasks = await js.load_archive_tasks()
            archived_assignments = await js.load_archive_assignments()
            archived_approvals = await js.load_archive_approvals()

            archived_task_ids = {t["taskId"] for t in archived_tasks}

            tasks += archived_tasks
            assignments += archived_assignments
            approvals += archived_approvals

        subtask_count_map = {}
        for t in tasks:
            if isinstance(t.get("subTaskId"), list):
                for parent_id in t["subTaskId"]:
                    subtask_count_map[parent_id] = (
                        subtask_count_map.get(parent_id, 0) + 1
                    )

        for task in tasks:
            task_id = task["taskId"]
            task_priority = await js.get_master_label_by_code(task.get("priority"))
            task_status = await js.get_master_label_by_code(task.get("status"))
            lead_user = user_map.get(task.get("leadId"))

            task_assignments = [a for a in assignments if a.get("taskId") == task_id]

            assignees = []
            for a in task_assignments:
                assign_user = user_map.get(a.get("assignTo"))
                assignees.append(
                    {
                        "taskAssignId": a.get("taskAssignId"),
                        "taskId": a.get("taskId"),
                        "assignTo": a.get("assignTo"),
                        "assignToName": (
                            assign_user.get("name") if assign_user else None
                        ),
                        "assigned_date": a.get("assigned_date"),
                        "eta_datetime": a.get("eta_datetime"),
                        "status": a.get("status"),
                        "workStatus": a.get("workStatus"),
                        "startedAt": a.get("startedAt"),
                        "completedAt": a.get("completedAt"),
                    }
                )

            task_approvals = []
            for ap in approvals:
                if ap.get("taskId") == task_id:
                    submitted_user = user_map.get(ap.get("submittedBy"))
                    reviewed_user = user_map.get(ap.get("reviewedBy"))

                    task_approvals.append(
                        {
                            "approvalId": ap.get("approvalId"),
                            "taskId": ap.get("taskId"),
                            "submittedBy": ap.get("submittedBy"),
                            "submittedByName": (
                                submitted_user.get("name") if submitted_user else None
                            ),
                            "reviewedBy": ap.get("reviewedBy"),
                            "reviewedByName": (
                                reviewed_user.get("name") if reviewed_user else None
                            ),
                            "status": ap.get("status"),
                            "reviewComment": ap.get("reviewComment"),
                            "reviewedAt": ap.get("reviewedAt"),
                        }
                    )

            result.append(
                {
                    "taskId": task_id,
                    "subTaskId": task.get("subTaskId"),
                    "totalSubTasks": subtask_count_map.get(task_id, 0),
                    "taskName": task.get("taskName"),
                    "taskdetail": task.get("taskdetail"),
                    "priority": task_priority,
                    "status": task_status,
                    "leadId": task.get("leadId"),
                    "leadBy": lead_user.get("name") if lead_user else None,
                    "assignee": assignees if assignees else None,
                    "approvals": task_approvals if task_approvals else None,
                    "createdAt": task.get("createdAt"),
                    "createdBy": task.get("createdBy"),
                    "isRestore": task_id in archived_task_ids,
                }
            )

        return result
    except Exception as e:
        return []


async def get_main_tasks_async(showArchive=False):
    try:
        tasks = await get_all_tasks_async(showArchive)
        tasks = [t for t in tasks if t.get("subTaskId") is None]
        return success(tasks)

    except Exception as e:
        return error(str(e), 500)


async def get_sub_tasks_by_TaskId_async(taskId, showArchive=False):
    try:
        tasks = await get_all_tasks_async(showArchive)
        sub_tasks = [
            t
            for t in tasks
            if isinstance(t.get("subTaskId"), list) and taskId in t["subTaskId"]
        ]
        return success(sub_tasks)

    except Exception as e:
        return error(str(e), 500)


async def get_task_by_TaskId_async(taskId):
    try:
        task = await js.get_tasks_by_key(taskId)
        if not task:
            return error("Task not found", 404)
        return success(task)
    except Exception as e:
        return error(str(e), 500)


async def add_edit_task_async(task_data, task_id=None):
    try:
        tasks = await js.load_tasks()

        if task_id is not None and task_id > 0:
            index = next(
                (i for i, u in enumerate(tasks) if u["taskId"] == task_id), None
            )
            if index is None:
                return error("Task not found", 404)

            tasks[index].update(task_data)

            await js.save_tasks(tasks)
            return success(data=tasks[index], message="Task Updated Successfully!")
        else:
            # ---------------- ADD ----------------
            if tasks:
                max_id = max(u["taskId"] for u in tasks)
                new_task_id = max_id + 1
            else:
                new_task_id = 1  # start from 1 if no users exist

            task_data["taskId"] = new_task_id

            if any(u["taskId"] == new_task_id for u in tasks):
                return error("Task with this ID already exists", 400)

            tasks.append(task_data)
            await js.save_tasks(tasks)
            return success(data=task_data, message="Task Added Successfully!")
    except Exception as e:
        return error(str(e), 500)


async def remove_task_by_id_async(task_id):
    try:
        tasks = await js.load_tasks()

        # Find the user to delete
        task_to_delete = next((u for u in tasks if u["taskId"] == task_id), None)
        if not task_to_delete:
            return error("Task not found", 404)

        # Filter out the user
        new_task = [u for u in tasks if u["taskId"] != task_id]
        await js.save_tasks(new_task)

        task_name = task_to_delete.get("taskName", str(task_id))
        return success(
            data=new_task, message=f"Task '{task_name}' removed successfully"
        )
    except Exception as e:
        return error(str(e), 500)


async def get_admin_panel_dropdown_async():
    try:
        drpRoles = []
        roles = await js.load_roles()
        for role in roles:
            drpRoles.append(
                {
                    "code": role["roleId"],
                    "label": role["rolename"],
                }
            )

        master_data = await js.load_master()
        drpWorkStatus = master_data.get("workStatus", [])
        drpTaskStatus = master_data.get("taskStatus", [])
        drpTaskPriority = master_data.get("priority", [])
        drpEntityType = master_data.get("entityType", [])

        drpSubTasks = []
        tasks = await js.load_tasks()
        for task in tasks:
            drpSubTasks.append(
                {
                    "code": task["taskId"],
                    "label": task["taskName"],
                }
            )

        drpUsers = []
        users = await js.load_users()
        for user in users:
            drpUsers.append(
                {
                    "code": user["userId"],
                    "label": user["name"],
                }
            )

        result = {
            "drpRoles": drpRoles,
            "drpWorkStatus": drpWorkStatus,
            "drpTaskStatus": drpTaskStatus,
            "drpTaskPriority": drpTaskPriority,
            "drpEntityType": drpEntityType,
            "drpSubTasks": drpSubTasks,
            "drpUsers": drpUsers,
        }
        return success(result)
    except Exception as e:
        return error(str(e), 500)


async def get_assignment_by_TaskId_async(taskId):
    try:
        result = []
        assignments = await js.load_assignments()
        task_assignments = [a for a in assignments if a.get("taskId") == taskId]
        for assignment in task_assignments:
            data = await get_assignment_approval_map_async(assignment)
            result.append(data)

        return success(result)
    except Exception as e:
        return error(str(e), 500)


async def get_assignment_by_TaskId_AssignTo_async(taskId, assignTo):
    try:
        assignments = await js.load_assignments()
        task_assignment = next(
            (
                a
                for a in assignments
                if a.get("taskId") == taskId and a.get("assignTo") == assignTo
            ),
            None,
        )
        response = await get_assignment_approval_map_async(task_assignment)
        return success(response)
    except Exception as e:
        return error(str(e), 500)


async def get_assignment_approval_map_async(assignment):
    if assignment is None:
        return error("Assignment not found", 404)

    approvals = await js.load_approvals()
    taskId = assignment.get("taskId")

    approval = next(
        (
            ap
            for ap in approvals
            if ap.get("taskId") == taskId
            and ap.get("submittedBy") == assignment.get("assignTo")
        ),
        None,
    )

    # ----------------- Date Resolution -----------------
    assigned_date = js.parse_date(assignment.get("assigned_date"))
    started_at = js.parse_date(assignment.get("startedAt"))
    completed_at = js.parse_date(assignment.get("completedAt"))
    eta_date = js.parse_date(assignment.get("eta_datetime"))

    now = datetime.now(timezone.utc)

    start_date = started_at or assigned_date
    end_date = completed_at or now

    # ----------------- Duration -----------------
    duration = None
    if start_date:
        diff = end_date - start_date
        duration = {
            "days": diff.days,
            "hours": diff.seconds // 3600,
            "minutes": (diff.seconds % 3600) // 60,
        }

    # ----------------- ETA Status -----------------
    durationMsg = "ETA not set"
    remainingDays = None
    etaStatus = "NONE"

    if eta_date and start_date:
        compare_date = completed_at or now
        remaining = eta_date - compare_date
        remainingDays = remaining.days

        if completed_at:
            if completed_at <= eta_date:
                durationMsg = "Completed within ETA"
                etaStatus = "COMPLETED_ON_TIME"
            else:
                durationMsg = "Completed after ETA"
                etaStatus = "COMPLETED_LATE"
        else:
            if remaining.total_seconds() >= 0:
                durationMsg = "ETA on track"
                etaStatus = "ON_TRACK"
            else:
                durationMsg = "ETA exceeded"
                etaStatus = "EXCEEDED"

    submitted_user = None
    reviewed_user = None

    if approval:
        if approval.get("submittedBy"):
            submitted_user = await js.get_user_by_key(approval.get("submittedBy"))

        if approval.get("reviewedBy"):
            reviewed_user = await js.get_user_by_key(approval.get("reviewedBy"))

    # ----------------- Approval Flattening -----------------
    response = {
        "taskAssignId": assignment.get("taskAssignId"),
        "taskId": assignment.get("taskId"),
        "assignTo": assignment.get("assignTo"),
        "status": assignment.get("status"),
        "workStatus": assignment.get("workStatus"),
        "assigned_date": assignment.get("assigned_date"),
        "startedAt": assignment.get("startedAt"),
        "completedAt": assignment.get("completedAt"),
        "eta_datetime": assignment.get("eta_datetime"),
        # computed fields for UI
        "duration": duration,
        "durationMsg": durationMsg,
        "remainingDays": remainingDays,
        "etaStatus": etaStatus,
        # approval (flattened)
        "approvalStatus": approval.get("status") if approval else None,
        "submittedBy": submitted_user.get("name") if submitted_user else None,
        "submitComment": approval.get("submitComment") if approval else None,
        "submittedAt": approval.get("submittedAt") if approval else None,
        "reviewedBy": reviewed_user.get("name") if reviewed_user else None,
        "reviewComment": approval.get("reviewComment") if approval else None,
        "reviewedAt": approval.get("reviewedAt") if approval else None,
    }

    return response


async def add_edit_assignments_async(assignments_data):
    try:
        if not isinstance(assignments_data, list):
            return error("Payload must be a list of assignments", 400)

        assignments = await js.load_assignments()
        max_assign_id = max((a.get("taskAssignId", 0) for a in assignments), default=0)

        saved_items = []
        for item in assignments_data:
            task_assign_id = item.get("taskAssignId", 0)

            # ---------------- DELETE ----------------
            if item.get("isRemoved") is True:
                if task_assign_id > 0:
                    assignments = [
                        a
                        for a in assignments
                        if a.get("taskAssignId") != task_assign_id
                    ]
                continue

            # ---------------- UPDATE ----------------
            if task_assign_id > 0:
                existing = next(
                    (a for a in assignments if a.get("taskAssignId") == task_assign_id),
                    None,
                )

                if not existing:
                    return error(f"Assignment {task_assign_id} not found", 404)

                existing.update(
                    {
                        "taskId": item.get("taskId"),
                        "assignTo": item.get("assignTo"),
                        "status": item.get("status"),
                        "workStatus": item.get("workStatus"),
                        "assigned_date": item.get("assigned_date"),
                        "eta_datetime": item.get("eta_datetime"),
                        "startedAt": item.get("startedAt"),
                        "completedAt": item.get("completedAt"),
                    }
                )
                saved_items.append(existing)

            # ---------------- ADD ----------------
            else:
                max_assign_id += 1
                new_item = {
                    "taskAssignId": max_assign_id,
                    "taskId": item.get("taskId"),
                    "assignTo": item.get("assignTo"),
                    "status": item.get("status"),
                    "workStatus": item.get("workStatus"),
                    "assigned_date": item.get("assigned_date"),
                    "eta_datetime": item.get("eta_datetime"),
                    "startedAt": item.get("startedAt"),
                    "completedAt": item.get("completedAt"),
                }

                assignments.append(new_item)
                saved_items.append(new_item)

        await js.save_assignments_tasks(assignments)

        return success(data=saved_items, message="Assignments saved successfully!")
    except Exception as e:
        return error(str(e), 500)

async def archive_restore_task_async(taskId, isSubTask=False, restoreTask=False):
    try:
        # Load main data
        tasks = await js.load_tasks()
        assignments = await js.load_assignments()
        approvals = await js.load_approvals()

        # Load archive data
        archived_tasks = await js.load_archive_tasks()
        archived_assignments = await js.load_archive_assignments()
        archived_approvals = await js.load_archive_approvals()

        # -----------------------------
        # Helper: find subtasks
        # -----------------------------
        def get_subtask_ids(parent_id, task_list):
            return [
                t["taskId"]
                for t in task_list
                if isinstance(t.get("subTaskId"), list) and parent_id in t["subTaskId"]
            ]

        # -----------------------------
        # RESTORE TASK
        # -----------------------------
        if restoreTask:
            restore_task_ids = [taskId]

            if isSubTask:
                restore_task_ids += get_subtask_ids(taskId, archived_tasks)

            # Restore tasks
            restored_tasks = [t for t in archived_tasks if t["taskId"] in restore_task_ids]
            tasks.extend(restored_tasks)
            archived_tasks[:] = [t for t in archived_tasks if t["taskId"] not in restore_task_ids]

            # Restore assignments
            restored_assignments = [a for a in archived_assignments if a["taskId"] in restore_task_ids]
            assignments.extend(restored_assignments)
            archived_assignments[:] = [a for a in archived_assignments if a["taskId"] not in restore_task_ids]

            # Restore approvals
            restored_approvals = [a for a in archived_approvals if a["taskId"] in restore_task_ids]
            approvals.extend(restored_approvals)
            archived_approvals[:] = [a for a in archived_approvals if a["taskId"] not in restore_task_ids]

            await js.save_tasks(tasks)
            await js.save_assignments_tasks(assignments)
            await js.save_approvals(approvals)

            await js.save_archive_tasks(archived_tasks)
            await js.save_archive_assignments(archived_assignments)
            await js.save_archive_approvals(archived_approvals)

            return success(message="Task restored successfully")

        # -----------------------------
        # ARCHIVE TASK
        # -----------------------------
        archive_task_ids = [taskId]

        if isSubTask:
            archive_task_ids += get_subtask_ids(taskId, tasks)

        # Archive tasks
        move_tasks = [t for t in tasks if t["taskId"] in archive_task_ids]
        archived_tasks.extend(move_tasks)
        tasks[:] = [t for t in tasks if t["taskId"] not in archive_task_ids]

        # Archive assignments
        move_assignments = [a for a in assignments if a["taskId"] in archive_task_ids]
        archived_assignments.extend(move_assignments)
        assignments[:] = [a for a in assignments if a["taskId"] not in archive_task_ids]

        # Archive approvals
        move_approvals = [a for a in approvals if a["taskId"] in archive_task_ids]
        archived_approvals.extend(move_approvals)
        approvals[:] = [a for a in approvals if a["taskId"] not in archive_task_ids]

        await js.save_tasks(tasks)
        await js.save_assignments_tasks(assignments)
        await js.save_approvals(approvals)

        await js.save_archive_tasks(archived_tasks)
        await js.save_archive_assignments(archived_assignments)
        await js.save_archive_approvals(archived_approvals)

        return success(message="Task archived successfully")

    except Exception as e:
        return error(str(e), 500)