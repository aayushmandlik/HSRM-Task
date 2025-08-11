from fastapi import APIRouter, Depends
from typing import List
from schemas.leave_schema import LeaveResponse, LeaveUpdateStatus
from core.security import require_admin, TokenPayload
from services.admin_leave_service import *

router = APIRouter(prefix="/admin/leave", tags=["Admin Leave"])

@router.get("/leaverequests", response_model=List[LeaveResponse])
async def get_leave_requests(current_admin: TokenPayload = Depends(require_admin)):
    return await get_all_leave_requests()

@router.get("/pendingrequests", response_model=List[LeaveResponse])
async def get_pending_leave_requests(current_admin: TokenPayload = Depends(require_admin)):
    return await fetch_pending_leave_requests()

@router.put("/{leave_id}/status", response_model=LeaveResponse)
async def update_leave_status(
    leave_id: str,
    leave_update: LeaveUpdateStatus,
    current_admin: TokenPayload = Depends(require_admin)
):
    return await update_leave_status_service(leave_id, leave_update)
