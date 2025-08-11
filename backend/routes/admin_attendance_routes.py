from fastapi import APIRouter, Depends, HTTPException
from core.security import require_admin
from schemas.token_schema import TokenPayload
from services.admin_attendance_service import fetch_all_attendance_logs

router = APIRouter(prefix="/admin/attendance", tags=["Admin Attendance"])

@router.get("/logs")
async def get_all_logs(
    current_user: TokenPayload = Depends(require_admin),
    date: str = None
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    return await fetch_all_attendance_logs(date)