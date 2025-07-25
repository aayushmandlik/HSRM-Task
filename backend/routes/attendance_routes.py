from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from databases.database import attendance_collection, employee_collection
from bson.objectid import ObjectId
from core.security import get_current_user, require_admin_or_user, require_admin
from schemas.attendance_schema import Attendance, AttendanceStatus
from schemas.token_schema import TokenPayload
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/checkin")
async def check_in(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id
    today = datetime.now().date()

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_in": {"$gte": datetime(today.year, today.month, today.day)}
    })

    if record:
        raise HTTPException(status_code=400, detail="Already checked in today")

    await attendance_collection.insert_one({
        "user_id": user_id,
        "check_in": datetime.now(),
        "check_out": None,
        "break_in": None,
        "break_out": None,
        "status": AttendanceStatus.PRESENT,
        "total_hours": None
    })

    return {"message": "Check-in successful"}

@router.post("/checkout")
async def check_out(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id
    now = datetime.now()

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None
    })

    if not record:
        raise HTTPException(status_code=404, detail="No active check-in")

    check_in = record["check_in"]
    break_in = record.get("break_in")
    break_out = record.get("break_out")
    total_hours = (now - check_in).total_seconds() / 3600
    if break_in and break_out:
        break_duration = (break_out - break_in).total_seconds() / 3600
        total_hours -= break_duration

    await attendance_collection.update_one(
        {"_id": record["_id"]},
        {"$set": {
            "check_out": now,
            "total_hours": round(total_hours, 2),
            "status": AttendanceStatus.PRESENT
        }}
    )

    return {"message": "Check-out successful"}

@router.post("/breakin")
async def break_in(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None,
        "break_in": None
    })

    if not record or record.get("break_out"):
        raise HTTPException(status_code=400, detail="Cannot start break or break already in progress")

    await attendance_collection.update_one(
        {"_id": record["_id"]},
        {"$set": {"break_in": datetime.now()}}
    )

    return {"message": "Break-in successful"}

@router.post("/breakout")
async def break_out(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None,
        "break_in": {"$ne": None},
        "break_out": None
    })

    if not record:
        raise HTTPException(status_code=400, detail="No active break to end")

    await attendance_collection.update_one(
        {"_id": record["_id"]},
        {"$set": {"break_out": datetime.now()}}
    )

    return {"message": "Break-out successful"}

@router.get("/logs/me")
async def get_my_logs(current_user: TokenPayload = Depends(require_admin_or_user)):
    try:
        user_id = current_user.user_id
        logs = await attendance_collection.find({"user_id": user_id}).to_list(length=100)
        if not logs:
            logger.info(f"No attendance logs found for user_id: {user_id}")
            return {"logs": []}

        employee = await employee_collection.find_one({"user_id": user_id})
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
            del log["_id"] 
            processed_logs.append(Attendance(**log_dict))

        logger.info(f"Successfully retrieved {len(processed_logs)} logs for user_id: {user_id}")
        return {"logs": processed_logs}
    except Exception as e:
        logger.error(f"Error in get_my_logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")