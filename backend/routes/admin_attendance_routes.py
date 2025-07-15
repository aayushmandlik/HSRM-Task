from fastapi import APIRouter, Depends, HTTPException
from databases.database import attendance_collection
from core.security import require_admin
from schemas.token_schema import TokenPayload

router = APIRouter(prefix="/admin/attendance", tags=["Admin Attendance"])

@router.get("/logs")
async def get_all_logs(current_user: TokenPayload = Depends(require_admin)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    logs = await attendance_collection.find({}).to_list(length=100)
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"logs": logs}