from databases.database import attendance_collection, employee_collection
from datetime import datetime
from typing import Optional
from schemas.attendance_schema import AttendanceStatus

async def find_today_checkin(user_id: str, today: datetime):
    return await attendance_collection.find_one({
        "user_id": user_id,
        "check_in": {"$gte": datetime(today.year, today.month, today.day)}
    })

async def insert_checkin(user_id: str):
    return await attendance_collection.insert_one({
        "user_id": user_id,
        "check_in": datetime.now(),
        "check_out": None,
        "break_in": None,
        "break_out": None,
        "status": AttendanceStatus.PRESENT,
        "total_hours": None
    })

async def find_active_attendance(user_id: str):
    return await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None
    })

async def update_checkout(record_id, now, total_hours):
    return await attendance_collection.update_one(
        {"_id": record_id},
        {"$set": {
            "check_out": now,
            "total_hours": round(total_hours, 2),
            "status": "PRESENT"
        }}
    )

async def find_for_break_in(user_id: str):
    return await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None,
        "break_in": None
    })

async def update_break_in(record_id):
    return await attendance_collection.update_one(
        {"_id": record_id},
        {"$set": {"break_in": datetime.now()}}
    )

async def find_for_break_out(user_id: str):
    return await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None,
        "break_in": {"$ne": None},
        "break_out": None
    })

async def update_break_out(record_id):
    return await attendance_collection.update_one(
        {"_id": record_id},
        {"$set": {"break_out": datetime.now()}}
    )

async def find_logs(user_id: str):
    return await attendance_collection.find({"user_id": user_id}).to_list(length=100)

async def find_employee(user_id: str):
    return await employee_collection.find_one({"user_id": user_id})
