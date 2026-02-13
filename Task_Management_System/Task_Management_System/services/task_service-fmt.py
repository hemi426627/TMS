from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import success, error
import asyncio


async def get_tasks_async(subTask=False, showArchive=False):
    try:
        result = []

        tasks = await js.load_tasks()
        assignments = await js.load_assignments()
        approvals = await js.load_approvals()
        users = await js.load_users()

        if showArchive:
            archive_tasks = await js.load_archive_tasks()
            archive_assignments = await js.load_archive_assignments()
            archive_approvals = await js.load_archive_approvals()

            tasks += archive_tasks
            assignments += archive_assignments
            approvals += archive_approvals

        if subTask:
            main_tasks = [t for t in tasks if t.get("subTaskId")]
        else:
            main_tasks = [t for t in tasks if not t.get("subTaskId")]

        for task in main_tasks:
            task_id = task["taskId"]

            task_assignments = await get_assignments_by_task(task_id)
            print("Assignment:", task_assignments)

            # Get approval(s)
            task_approval = await js.get_approvals_by_key(itemValue=task_id, key="taskId")
            if task_approval:
                user_id = task_approval.get("assignTo")  # ensure key matches your data
                task_user = await js.get_user_by_key(itemValue=user_id, key="userId")
            else:
                task_user = None

            task_assignments = await js.get_assignments_by_task(task_id)
            task_approvals = await js.get_approvals_by_task(task_id)
            
            task_users = []
            for approval in task_approvals:
                user = await js.get_user_by_key(itemValue=approval.get("assignTo"), key="userId")
                if user:
                    task_users.append(user)
    
            print("Approval:", task_approval)
            print("User:", task_user)
            
            result.append(
                {
                    "taskId": task_id,
                    "subTaskId": task.get("subTaskId"),
                    "taskName": task.get("taskName"),
                    "taskdetail": task.get("taskdetail"),
                    "priority": task.get("priority"),
                    # "mainTaskStatus": main_status,
                    # "Assignee": assignees,
                    # "approvals": approvals_for_task,
                    # "leadId": lead_id,
                    # "leadName": lead_name,
                    "createdAt": task.get("createdAt"),
                    "createdBy": task.get("createdBy"),
                }
            )

        return success(result)

    except Exception as e:
        return error(str(e), 500)


async def get_tasks_async1(subTask=False, showArchive=False):
    try:
        # Load active tasks
        tasks = await js.load_tasks()
        assignments = await js.load_assignments()
        approvals = await js.load_approvals()
        users = await js.load_users()

        all_tasks = tasks
        all_assignments = assignments
        all_approvals = approvals

        if showArchive:
            # Load archived data
            archive_tasks = await js.load_archive_tasks()
            archive_assignments = await js.load_archive_assignments()
            archive_approvals = await js.load_archive_approvals()

            all_tasks += archive_tasks
            all_assignments += archive_assignments
            all_approvals += archive_approvals

        # Build user map for names
        user_map = {
            u["userId"]: u.get("name", u.get("username", f"User-{u['userId']}"))
            for u in users
        }

        # Build task map for sub-task lookup
        task_map = {t["taskId"]: t for t in all_tasks}

        # Determine which tasks to include
        if not subTask:
            # Only main tasks (exclude tasks that are sub-tasks of another task)
            sub_task_ids = [
                sid for t in all_tasks for sid in (t.get("subTaskId") or [])
            ]
            tasks_to_return = [t for t in all_tasks if t["taskId"] not in sub_task_ids]
        else:
            # Return all tasks including sub-tasks
            tasks_to_return = all_tasks

        result = []

        for task in tasks_to_return:
            task_id = task.get("taskId")
            sub_ids = task.get("subTaskId") or []

            # Sub-task names
            sub_names = [task_map[s]["taskName"] for s in sub_ids if s in task_map]

            # Get assignments for this task and sub-tasks
            related_task_ids = [task_id] + sub_ids
            task_assigns = [
                a for a in all_assignments if a["taskId"] in related_task_ids
            ]

            assignees = []
            for a in task_assigns:
                assign_to_id = a.get("assignTo")
                assignees.append(
                    {
                        "taskAssignId": a.get("taskAssignId"),
                        "taskId": a.get("taskId"),
                        "assignTo": assign_to_id,
                        "assignToName": user_map.get(
                            assign_to_id, f"User-{assign_to_id}"
                        ),
                        "assigned_date": a.get("assigned_date"),
                        "eta_datetime": a.get("eta_datetime"),
                        "start_date": a.get("start_date"),
                        "end_date": a.get("end_date"),
                        "status": a.get("status"),
                        "workStatus": a.get("workStatus"),
                        "startedAt": a.get("startedAt"),
                        "completedAt": a.get("completedAt"),
                    }
                )

            # Get approvals for task and sub-tasks
            task_approvals = [
                ap for ap in all_approvals if ap["taskId"] in related_task_ids
            ]

            # Determine mainTaskStatus
            main_status = None
            if task_approvals:
                latest_approval = max(
                    task_approvals, key=lambda x: x.get("reviewedAt") or ""
                )
                main_status = latest_approval.get("status")
            elif assignees:
                latest_assign = max(
                    assignees, key=lambda x: x.get("assigned_date") or ""
                )
                main_status = latest_assign.get("workStatus")
            else:
                main_status = task.get("status")

            lead_id = task.get("leadId")
            lead_name = user_map.get(lead_id, f"User-{lead_id}")

            result.append(
                {
                    "taskId": task_id,
                    "subTaskId": sub_ids if sub_ids else None,
                    "subTaskNames": sub_names if sub_names else None,
                    "taskName": task.get("taskName"),
                    "taskdetail": task.get("taskdetail"),
                    "priority": task.get("priority"),
                    "mainTaskStatus": main_status,
                    "Assignee": assignees if assignees else [],
                    "approvals": task_approvals if task_approvals else [],
                    "leadId": lead_id,
                    "leadName": lead_name,
                    "createdAt": task.get("createdAt"),
                    "createdBy": task.get("createdBy"),
                }
            )

        return success(result)

    except Exception as e:
        return error(str(e), 500)

async def get_assignments_by_task(task_id):
    assignments = await js.load_assignments()
    return [a for a in assignments if a.get("taskId") == task_id]

async def get_approvals_by_task(task_id):
    approvals = await js.load_approvals()
    return [a for a in approvals if a.get("taskId") == task_id]
