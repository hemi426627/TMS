from asyncio.windows_events import NULL
from xml.sax import parseString
from Task_Management_System.services import json_service as js
from Task_Management_System.services.response_helpers import *
from Task_Management_System.services.task_service import *
from datetime import datetime, date, timezone
from collections import defaultdict
import asyncio

async def get_assignment_approval_detail_async(task_id=None,user_id=None):
    try:
        result = []
                
        assignments = await js.load_assignments() or []
        approvals = await js.load_approvals() or []

        for assignment in assignments:
            taskAssignId = (assignment.get("taskAssignId") if assignment else None)
            taskId = (assignment.get("taskId") if assignment else None)
           
            approval = next((ap for ap in approvals if ap.get("taskAssignId") == taskAssignId), None)

            assignTo = assignment.get("assignTo") if assignment else None
            assignToName = await js.get_name_by_userid(assignTo) if assignTo else None

            work_status_code = (assignment.get("workStatus") if assignment else None)
            status_code = assignment.get("status") if assignment else None
            approval_status_code = approval.get("status") if approval else None

            work_status = (await js.get_master_label_by_code(work_status_code) if work_status_code else None)
            status = await js.get_master_label_by_code(status_code) if status_code else None
            approval_status = (await js.get_master_label_by_code(approval_status_code) if approval_status_code else None)

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

            if ((task_id is None or taskId == task_id) and (user_id is None or assignTo == user_id)):
                result.append({                 
                    "taskAssignId": taskAssignId,
                    "taskId": taskId,
                    
                    "assignTo": assignTo,
                    "assignToName": assignToName,
                    
                    "work_status_code": work_status_code,
                    "work_status": work_status,
                    
                    "status_code": status_code,
                    "status": status,
                    
                    "assigned_date": assigned_date,
                    
                    "startedAt": started_at,
                    "completedAt": completed_at,
                    
                    "eta_datetime": eta_date,
                    "duration": duration,
                    "durationMsg": durationMsg,
                    "remainingDays": remainingDays,
                    "etaStatus": etaStatus,

                    "approval_status_code": approval_status_code,
                    "approval_status": approval_status,
                    
                    "submittedBy": (approval.get("submittedBy") if approval else None),
                    "submitted_user": (submitted_user.get("name") if submitted_user else None),
                    "submitComment": (approval.get("submitComment") if approval else None),
                    "submittedAt": (approval.get("submittedAt") if approval else None),

                    "reviewedBy": (approval.get("reviewedBy") if approval else ""),
                    "reviewed_user": (reviewed_user.get("name") if reviewed_user else ""),

                    "reviewComment": (approval.get("reviewComment") if approval else None),
                    "reviewedAt": (approval.get("reviewedAt") if approval else None),
                })

        return result

    except Exception as e:
        print("Error in get_assignment_approval_detail_async:", e)
        return []

async def get_tasks_detail_async(user_id=None):
    try:
        result = []

        tasks = await js.load_tasks() or []
        
        subtask_count_map = defaultdict(int)
        for t in tasks:
            subtask_ids = t.get("subTaskId") or []
            if isinstance(subtask_ids, list):
                for parent_id in subtask_ids:
                    subtask_count_map[parent_id] += 1

        for task in tasks:
            taskId = task.get("taskId")

            leadId = task.get("leadId")
            leadBy = await js.get_name_by_userid(leadId)
            isLead = (user_id is not None and leadId == user_id)
            
            main_status_code = task.get("status")
            main_status = (await js.get_master_label_by_code(main_status_code) if main_status_code else None)
            
            priority_code = task.get("priority")
            priority = (await js.get_master_label_by_code(priority_code) if priority_code else None)

            if user_id is None or isLead:
                assignments = await get_assignment_approval_detail_async(taskId) or []
            else:
                assignments = await get_assignment_approval_detail_async(taskId, user_id) or []
                
            for assignment in assignments:
                result.append({
                    "taskId": taskId,
                    
                    "subTaskId": task.get("subTaskId") or [],
                    "totalSubTasks": subtask_count_map.get(taskId, 0),
                    
                    "taskName": task.get("taskName"),
                    "taskdetail": task.get("taskdetail"),
                    
                    "leadId": leadId,
                    "leadBy": leadBy,
                    "isLead": isLead,
                    
                    "main_status_code": main_status_code,
                    "main_status": main_status,
                    
                    "priority_code": priority_code,
                    "priority": priority,

                    "taskAssignId": (assignment.get("taskAssignId") if assignment else None),
                    
                    "assignTo": (assignment.get("assignTo") if assignment else None),
                    "assignToName": (assignment.get("assignToName") if assignment else None),
                    
                    "work_status_code": (assignment.get("work_status_code") if assignment else None),
                    "work_status": (assignment.get("work_status") if assignment else None),
                    
                    "status_code": (assignment.get("status_code") if assignment else None),
                    "status": (assignment.get("status") if assignment else None),
                    
                    "assigned_date": (assignment.get("assigned_date") if assignment else None),
                    
                    "startedAt": (assignment.get("startedAt") if assignment else None),
                    "completedAt": (assignment.get("completedAt") if assignment else None),
                    
                    "eta_datetime": (assignment.get("eta_datetime") if assignment else None),
                    "duration": (assignment.get("duration") if assignment else None),
                    "durationMsg": (assignment.get("durationMsg") if assignment else None),
                    "remainingDays": (assignment.get("remainingDays") if assignment else None),
                    "etaStatus": (assignment.get("etaStatus") if assignment else None),

                    "approval_status_code": (assignment.get("approval_status_code") if assignment else None),
                    "approval_status": (assignment.get("approval_status") if assignment else None),
                    
                    "submittedBy": (assignment.get("submittedBy") if assignment else None),
                    "submitted_user": (assignment.get("submitted_user") if assignment else None),
                    "submitComment": (assignment.get("submitComment") if assignment else None),
                    "submittedAt": (assignment.get("submittedAt") if assignment else None),

                    "reviewedBy": (assignment.get("reviewedBy") if assignment else None),
                    "reviewed_user": (assignment.get("reviewed_user") if assignment else None),

                    "reviewComment": (assignment.get("reviewComment") if assignment else None),
                    "reviewedAt": (assignment.get("reviewedAt") if assignment else None),

                    "createdAt": task.get("createdAt"),
                    "createdBy": task.get("createdBy"),
                })         

        return result
    except Exception as e:
        print("Error in get_tasks_detail_async:", e)
        return []

async def get_user_main_tasks_async():
    try:
        session_user = js.get_session_user()
        if not session_user:
            return []

        role_id = session_user.get("roleId")

        user_id = session_user.get("userId")
        user_name = await js.get_name_by_userid(user_id)

        if role_id in (1, 2):
            tasks = await get_tasks_detail_async()
        else:
            tasks = await get_tasks_detail_async(user_id)

        tasks_status = [
            {"status_code": "ASSIGNED", "status": "Assigned", "seq": 1},
            {"status_code": "NOT_STARTED", "status": "Not Started", "seq": 2},
            {"status_code": "IN_PROGRESS", "status": "In Progress", "seq": 3},
            {"status_code": "COMPLETED", "status": "Completed", "seq": 4},
            {"status_code": "REVIEW", "status": "Task In Review", "seq": 5}
        ]

        tasks_by_status = {s["status_code"]: [] for s in tasks_status}
        status_counter = {s["status"]: 0 for s in tasks_status}  

        for task in tasks:
            work_status_code = task.get("work_status_code") or ""
            work_status_label = task.get("work_status") or ""

            status_code = task.get("status_code") or ""
            status_label = task.get("status") or ""

            target_status_code = status_code

            if work_status_code == "ASSIGNED":
                target_status_code = "ASSIGNED"
            elif status_code in ("NOT_STARTED", "IN_PROGRESS", "COMPLETED"):
                target_status_code = status_code

            if work_status_code in ("PENDING_APPROVAL"):
                target_status_code = "REVIEW"

            if target_status_code in tasks_by_status:
                tasks_by_status[target_status_code].append(task)
                frontend_label = next((s["status"] for s in tasks_status if s["status_code"] == target_status_code), target_status_code)
                status_counter[frontend_label] += 1

        response_data = {
            "tasks_status": tasks_status,       
            "tasks_by_status": tasks_by_status, 
            "status_counter": status_counter    
        }
        return success(response_data)
    except Exception as e:
        return error(str(e), 500)

async def get_user_daily_tasks_async():
    try:
        session_user = js.get_session_user()
        if not session_user:
            return []

        role_id = session_user.get("roleId")
        user_id = session_user.get("userId")

        # Load tasks
        if role_id in (1, 2):
            tasks = await get_tasks_detail_async()
        else:
            tasks = await get_tasks_detail_async(user_id)

        dailyTasks = await js.load_daily_tasks()

        tasks_status = [
            {"status_code": "Daily_TASKS", "status": "Daily Tasks", "seq": 1},
            {"status_code": "IN_PROGRESS", "status": "In Progress", "seq": 2},
            {"status_code": "COMPLETED", "status": "Completed", "seq": 3}
        ]

        tasks_by_status = {s["status_code"]: [] for s in tasks_status}
        status_counter = {s["status"]: 0 for s in tasks_status}

        today = date.today().strftime("%Y-%m-%d")

        # Today's daily task map → taskId => dailyTask
        today_daily_task_map = {
            d.get("taskId"): d
            for d in dailyTasks
            if d.get("date") == today
        }

        # 🔹 Loop over all tasks only ONCE
        for task in tasks:
            task_id = task.get("taskId")

            # CASE 1: Task exists in DailyTasks (today)
            if task_id in today_daily_task_map:
                daily = today_daily_task_map[task_id]
                target_status_code = daily.get("status_code") or "Daily_TASKS"

            # CASE 2: Task NOT in DailyTasks → show in Daily_TASKS
            else:
                target_status_code = "Daily_TASKS"

            if target_status_code in tasks_by_status:
                tasks_by_status[target_status_code].append(task)

                frontend_label = next(
                    (s["status"] for s in tasks_status if s["status_code"] == target_status_code),
                    target_status_code
                )
                status_counter[frontend_label] += 1

        response_data = {
            "tasks_status": tasks_status,
            "tasks_by_status": tasks_by_status,
            "status_counter": status_counter
        }

        return success(response_data)

    except Exception as e:
        return error(str(e), 500)

async def update_main_task_status_async(request_data):
    try:
        taskId = request_data.get("taskId")
        taskAssignId = request_data.get("taskAssignId")
        new_status = request_data.get("new_status")
        submitComment = request_data.get("submitComment") or ""
        reviewComment = request_data.get("reviewComment") or ""

        if not taskId or not taskAssignId or not new_status:
            return error("Invalid request data", 400)

        status_rules = {
            "NOT_STARTED": {
                "assignment": {
                    "taskAssignId": "SET",
                    "status": "NOT_STARTED",
                    "workStatus": "NOT_STARTED",
                    "startedAt": "",
                    "completedAt": ""
                },
                "approval": {
                    "action": "REMOVE" 
                },
                "task_status": "NOT_STARTED"
            },
        
            "IN_PROGRESS": {
                "assignment": {
                    "taskAssignId": "SET",
                    "status": "IN_PROGRESS",
                    "workStatus": "WORKING",
                    "startedAt": "NOW",
                    "completedAt": ""
                },
                "approval": {
                    "action": "REMOVE"  
                },
                "task_status": "WORKING"
            },
        
            "COMPLETED": {
                "assignment": {
                    "taskAssignId": "SET",
                    "status": "COMPLETED",
                    "workStatus": "PENDING_APPROVAL",
                    "startedAt": "KEEP",
                    "completedAt": "NOW"
                },
                "approval": {
                    "action": "ADD",  
                    "approvalId": "SET",
                    "taskAssignId": "SET",
                    "status": "PENDING_APPROVAL",
                    "submittedBy": "SET",
                    "submitComment": "SET",
                    "submittedAt": "NOW",
                    "reviewedBy": "",
                    "reviewComment": "",
                    "reviewedAt": ""
                },
                "task_status": "PENDING_APPROVAL"
            },
        
            "PENDING_APPROVAL": {
                "assignment": {
                    "taskAssignId": "SET",
                    "status": "COMPLETED",
                    "workStatus": "APPROVED",
                    "startedAt": "KEEP",
                    "completedAt": "KEEP"
                },
                "approval": {
                    "action": "UPDATE",  
                    "approvalId": "KEEP",
                    "taskAssignId": "KEEP",
                    "status": "APPROVED",
                    "submittedBy": "KEEP",
                    "submitComment": "KEEP",
                    "submittedAt": "KEEP",
                    "reviewedBy": "SET",
                    "reviewComment": "SET",
                    "reviewedAt": "NOW"
                },
                "task_status": "COMPLETED"
            },
        
            "REJECTED": {
                "assignment": {
                    "taskAssignId": "SET",
                    "status": "IN_PROGRESS",
                    "workStatus": "WORKING",
                    "startedAt": "KEEP",
                    "completedAt": ""
                },
                "approval": {
                    "action": "REMOVE" 
                },
                "task_status": "WORKING"
            }
        }

        if new_status not in status_rules:
            return error("Invalid status transition", 400)

        user_info = js.get_session_user()

        rule = status_rules[new_status]
        now = datetime.utcnow().isoformat(timespec="minutes")

        # ---------------- Load task ----------------
        tasks = await js.load_tasks()
        task = next((t for t in tasks if t.get("taskId") == taskId), None)
        if not task:
            return error("Task not found", 404)

        # ---------------- Build task update ----------------
        task_update = { "status": rule["task_status"] }

        # ---------------- task update ----------------
        await add_edit_task_async(task_update, taskId)

        # ---------------- Load assignment ----------------
        assignments = await js.load_assignments()
        assignment = next((a for a in assignments if a.get("taskAssignId") == taskAssignId), None)
        if not assignment:
            return error("Assignment not found", 404)

        # ---------------- Build assignment update ----------------
        assignment_update = assignment.copy()

        for key, value in rule["assignment"].items():
            if value == "NOW":
                assignment_update[key] = now
            elif value == "KEEP":
                assignment_update[key] = assignment.get(key)
            elif value == "SET":
                assignment_update[key] = taskAssignId
            else:
                assignment_update[key] = value
        
        # Ensure ID exists
        assignment_update["taskAssignId"] = taskAssignId
        
        # ---------------- assignment updates ----------------
        await add_edit_assignments_async([assignment_update]) 

         # ---------------- Load approvals ----------------
        approvals = await js.load_approvals()
        approval_action = rule.get("approval", {}).get("action")

        if approval_action == "REMOVE":
            approvals = [a for a in approvals if a.get("taskAssignId") != taskAssignId]
            await js.save_approvals(approvals)
        
        elif approval_action in ("ADD", "UPDATE"):
            approval = next((a for a in approvals if a.get("taskAssignId") == taskAssignId), None)
        
            if approval_action == "ADD" or not approval:
                approval_update = {}
                current_max = max([a.get("approvalId", 0) for a in approvals], default=0)
                next_approval_id = current_max + 1
                approval_update["approvalId"] = next_approval_id + 1
            else:
                approval_update = approval.copy()
        
            # Fill approval fields
            for key, value in rule["approval"].items():
                if key == "action":
                    continue  # skip action field
                if value == "NOW":
                    approval_update[key] = now
                elif value == "KEEP":
                    approval_update[key] = approval.get(key) if approval else None
                elif value == "SET":
                    if key == "taskAssignId":
                        approval_update[key] = taskAssignId
                    elif key == "approvalId":
                        approval_update[key] = next_approval_id
                    elif key in ("submittedBy", "reviewedBy"):
                        approval_update[key] = user_info.get("userId")
                    elif key == "submitComment":
                        approval_update[key] = submitComment
                    elif key == "reviewComment":
                        approval_update[key] = reviewComment
                    else:
                        approval_update[key] = ""  # default empty string
                else:
                    approval_update[key] = value
        
            # Add or update approval
            if approval_action == "ADD":
                approvals.append(approval_update)
            elif approval_action == "UPDATE" and approval:
                index = approvals.index(approval)
                approvals[index] = approval_update
        
            await js.save_approvals(approvals)

        return success(data = { "taskId": taskId, "taskAssignId": taskAssignId, "status": new_status}, message="Task status updated successfully!")
    except Exception as e:
        return error(str(e), 500)
