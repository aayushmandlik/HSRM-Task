from datetime import datetime
from bson.objectid import ObjectId
from schemas.attendance_schema import Attendance, AttendanceStatus
from repositories.admin_attendance_repository import *

async def fetch_all_attendance_logs(date=None):
    logs = await get_attendance_logs_by_date(date)
    log_map = {log["user_id"]: log for log in logs}

    employees = await get_all_employees()
    employee_logs = []

    filter_date = None
    if date:
        filter_date = datetime.strptime(date, "%Y-%m-%d").date()

    for emp in employees:
        if emp["status"] != "Active":
            continue

        emp_id = emp["user_id"]
        emp_name = emp.get("name", "Unknown")
        log = log_map.get(emp_id)

        if log:
            log["id"] = str(log["_id"])
            del log["_id"]

            if not log.get("check_in"):
                log["status"] = AttendanceStatus.ABSENT if (filter_date and filter_date < datetime.now().date()) else AttendanceStatus.NOT_MARKED
            elif log.get("check_in") and not log.get("check_out"):
                log["status"] = AttendanceStatus.PRESENT
            else:
                log["status"] = AttendanceStatus.PRESENT

            log["employee_name"] = emp_name
            employee_logs.append(Attendance(**log))
        else:
            status = AttendanceStatus.ABSENT if (filter_date and filter_date < datetime.now().date()) else AttendanceStatus.NOT_MARKED
            emp_attendance = {
                "id": str(ObjectId()),
                "user_id": emp_id,
                "check_in": None,
                "check_out": None,
                "break_in": None,
                "break_out": None,
                "status": status,
                "total_hours": None,
                "employee_name": emp_name
            }
            employee_logs.append(Attendance(**emp_attendance))

    return {"logs": employee_logs}
