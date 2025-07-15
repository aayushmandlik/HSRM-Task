from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from databases.database import attendance_collection
from bson.objectid import ObjectId
from core.security import get_current_user,require_admin_or_user
from schemas.attendance_schema import Attendance
from schemas.token_schema import TokenPayload


router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/checkin")
async def check_in(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id
    today = datetime.now().date()

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_in": { "$gte": datetime(today.year, today.month, today.day) }
    })

    if record:
        raise HTTPException(status_code=400, detail="Already checked in today")

    await attendance_collection.insert_one({
        "user_id": user_id,
        "check_in": datetime.now(),
        "check_out": None
    })

    return {"message": "Check-in successful"}

@router.post("/checkout")
async def check_out(current_user: TokenPayload = Depends(require_admin_or_user)):
    user_id = current_user.user_id

    record = await attendance_collection.find_one({
        "user_id": user_id,
        "check_out": None
    })

    if not record:
        raise HTTPException(status_code=404, detail="No active check-in")

    await attendance_collection.update_one(
        {"_id": record["_id"]},
        {"$set": { "check_out": datetime.now() }}
    )

    return {"message": "Check-out successful"}

@router.get("/logs/me")
async def get_my_logs(current_user: TokenPayload = Depends(require_admin_or_user)):
    logs = await attendance_collection.find({"user_id": current_user.user_id}).to_list(length=100)
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"logs": logs}
    
    
    