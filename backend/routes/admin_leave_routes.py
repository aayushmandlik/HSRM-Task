from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date, datetime
from bson import ObjectId
from schemas.leave_schema import LeaveResponse, LeaveUpdate, LeaveStatus
from databases.database import leave_collection
from core.security import require_admin, TokenPayload
from datetime import date

router = APIRouter(prefix="/admin/leave", tags=["Admin Leave"])

# Get all leave requests (Admin only)
@router.get("/leaverequests", response_model=List[LeaveResponse])
async def get_leave_requests(
    current_admin: TokenPayload = Depends(require_admin)
):
    leaves_cursor = leave_collection.find()
    leaves = []
    async for leave in leaves_cursor:
        leave["_id"] = str(leave["_id"])
        leaves.append(leave)
    return leaves


# Approve/Reject leave (Admin only)
@router.put("/{leave_id}/status", response_model=LeaveResponse)
async def update_leave_status(
    leave_id: str,
    leave_update: LeaveUpdate,
    current_admin: TokenPayload = Depends(require_admin)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        update_data = {"status": leave_update.status, "updated_at": datetime.utcnow()}
        await leave_collection.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": update_data}
        )
        
        updated_leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        updated_leave["_id"] = str(updated_leave["_id"])
        return updated_leave
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )