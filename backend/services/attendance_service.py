from datetime import datetime
from schemas.attendance_schema import Attendance, AttendanceStatus
from repositories import attendance_repository as repo
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def check_in(user_id: str):
    today = datetime.now().date()
    record = await repo.find_today_checkin(user_id, today)
    if record:
        raise HTTPException(status_code=400, detail="Already checked in today")
    await repo.insert_checkin(user_id)
    return {"message": "Check-in successful"}

async def check_out(user_id: str):
    now = datetime.now()
    record = await repo.find_active_attendance(user_id)
    if not record:
        raise HTTPException(status_code=404, detail="No active check-in")

    check_in_time = record["check_in"]
    total_hours = (now - check_in_time).total_seconds() / 3600

    if record.get("break_in") and record.get("break_out"):
        break_duration = (record["break_out"] - record["break_in"]).total_seconds() / 3600
        total_hours -= break_duration

    await repo.update_checkout(record["_id"], now, total_hours)
    return {"message": "Check-out successful"}

async def break_in(user_id: str):
    record = await repo.find_for_break_in(user_id)
    if not record or record.get("break_out"):
        raise HTTPException(status_code=400, detail="Cannot start break or break already in progress")
    await repo.update_break_in(record["_id"])
    return {"message": "Break-in successful"}

async def break_out(user_id: str):
    record = await repo.find_for_break_out(user_id)
    if not record:
        raise HTTPException(status_code=400, detail="No active break to end")
    await repo.update_break_out(record["_id"])
    return {"message": "Break-out successful"}

async def get_my_logs(user_id: str):
    try:
        logs = await repo.find_logs(user_id)
        if not logs:
            logger.info(f"No attendance logs found for user_id: {user_id}")
            return {"logs": []}

        employee = await repo.find_employee(user_id)
        employee_name = employee.get("name", "Unknown") if employee else "Unknown"

        processed_logs = []
        for log in logs:
            log_dict = {
                "id": str(log["_id"]),
                "user_id": log["user_id"],
                "check_in": log.get("check_in"),
                "check_out": log.get("check_out"),
                "break_in": log.get("break_in"),
                "break_out": log.get("break_out"),
                "status": log.get("status", AttendanceStatus.NOT_MARKED),
                "total_hours": log.get("total_hours"),
                "employee_name": employee_name
            }
            processed_logs.append(Attendance(**log_dict))

        logger.info(f"Retrieved {len(processed_logs)} logs for user_id: {user_id}")
        return {"logs": processed_logs}
    except Exception as e:
        logger.error(f"Error in get_my_logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

