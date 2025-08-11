from fastapi import APIRouter, Depends
from schemas.leave_schema import LeaveCreate, LeaveUpdate, LeaveResponse
from services import leave_service
from core.security import require_admin_or_user, TokenPayload
from typing import List

router = APIRouter(prefix="/Emp_leave", tags=["Employee Leave"])

@router.post("/request", response_model=LeaveResponse)
async def request_leave(leave: LeaveCreate, current_user: TokenPayload = Depends(require_admin_or_user)):
    return await leave_service.request_leave(leave, current_user)

@router.get("/my-requests", response_model=List[LeaveResponse])
async def get_my_leave_requests(current_user: TokenPayload = Depends(require_admin_or_user)):
    return await leave_service.get_my_leave_requests(current_user)

@router.patch("/{leave_id}", response_model=LeaveResponse)
async def update_leave_request(leave_id: str, update_data: LeaveUpdate, current_user: TokenPayload = Depends(require_admin_or_user)):
    return await leave_service.update_leave_request(leave_id, update_data, current_user)

@router.delete("/{leave_id}", response_model=LeaveResponse)
async def delete_leave_request(leave_id: str, current_user: TokenPayload = Depends(require_admin_or_user)):
    return await leave_service.delete_leave_request(leave_id, current_user)
