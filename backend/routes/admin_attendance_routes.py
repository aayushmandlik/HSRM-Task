from fastapi import APIRouter, Depends, HTTPException
from databases.database import attendance_collection,employee_collection
from core.security import require_admin
from schemas.token_schema import TokenPayload
from schemas.attendance_schema import AttendanceStatus,Attendance
from datetime import datetime,timedelta
from typing import Optional
from bson.objectid import ObjectId

router = APIRouter(prefix="/admin/attendance", tags=["Admin Attendance"])

@router.get("/logs")
async def get_all_logs(
    current_user: TokenPayload = Depends(require_admin),
    date: Optional[str] = None
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    # Determine target date range
    query = {}
    filter_date = None
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            query["check_in"] = {
                "$gte": datetime(filter_date.year, filter_date.month, filter_date.day),
                "$lt": datetime(filter_date.year, filter_date.month, filter_date.day) + timedelta(days=1)
            }
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Fetch all logs for the date (if provided)
    logs = await attendance_collection.find(query).to_list(length=1000)
    log_map = {log["user_id"]: log for log in logs}  # For faster lookup

    employees = await employee_collection.find().to_list(length=1000)
    employee_logs = []

    for emp in employees:
        emp_id = emp["user_id"]
        if emp["status"] == "Active":
            emp_name = emp.get("name", "Unknown") or emp.get("full_name", "Unknown")

        log = log_map.get(emp_id)

        if log:
            log["id"] = str(log["_id"])
            del log["_id"]

            if not log.get("check_in"):
                if filter_date and filter_date < datetime.now().date():
                    log["status"] = AttendanceStatus.ABSENT
                else:
                    log["status"] = AttendanceStatus.NOT_MARKED
            elif log.get("check_in") and not log.get("check_out"):
                log["status"] = AttendanceStatus.PRESENT
            else:
                log["status"] = AttendanceStatus.PRESENT  # or calculate based on logic
            log["employee_name"] = emp_name
            employee_logs.append(Attendance(**log))
        else:
            # No log exists at all for this employee on this date
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