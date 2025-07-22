from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date, datetime
from bson import ObjectId
from schemas.leave_schema import LeaveResponse, LeaveUpdateStatus, LeaveStatus
from databases.database import leave_collection
from core.security import require_admin, TokenPayload

router = APIRouter(prefix="/admin/leave", tags=["Admin Leave"])

# Get all leave requests (Admin only)
@router.get("/leaverequests", response_model=List[LeaveResponse])
async def get_leave_requests(
    current_admin: TokenPayload = Depends(require_admin)
):
    leaves_cursor = leave_collection.find()
    leaves = []
    async for leave in leaves_cursor:
        leave_data = {
            "_id": str(leave["_id"]),
            "employee_id": leave.get("employee_id", ""),
            "employee_name": leave.get("employee_name", ""),
            "start_date": leave.get("start_date").date() if leave.get("start_date") else date.today(),
            "end_date": leave.get("end_date").date() if leave.get("end_date") else date.today(),
            "leave_type": leave.get("leave_type", ""),
            "reason": leave.get("reason", ""),
            "status": LeaveStatus(leave.get("status", "pending")),
            "days": leave.get("days", 0),
            "created_at": leave.get("created_at") if leave.get("created_at") else datetime.utcnow(),
            "updated_at": leave.get("updated_at") if leave.get("updated_at") else datetime.utcnow(),
            "leave_taken": leave.get("leave_taken", 0),
            "remaining_leaves": leave.get("remaining_leaves", 20),
            "approved_by": leave.get("approved_by")
        }
        leaves.append(LeaveResponse(**leave_data))
    return leaves

# Get only pending leave requests (Admin only)
@router.get("/pendingrequests", response_model=List[LeaveResponse])
async def get_pending_leave_requests(
    current_admin: TokenPayload = Depends(require_admin)
):
    leaves_cursor = leave_collection.find({"status": "pending"})
    leaves = []
    async for leave in leaves_cursor:
        leave_data = {
            "_id": str(leave["_id"]),
            "employee_id": leave.get("employee_id", ""),
            "employee_name": leave.get("employee_name", ""),
            "start_date": leave.get("start_date").date() if leave.get("start_date") else date.today(),
            "end_date": leave.get("end_date").date() if leave.get("end_date") else date.today(),
            "leave_type": leave.get("leave_type", ""),
            "reason": leave.get("reason", ""),
            "status": LeaveStatus(leave.get("status", "pending")),
            "days": leave.get("days", 0),
            "created_at": leave.get("created_at") if leave.get("created_at") else datetime.utcnow(),
            "updated_at": leave.get("updated_at") if leave.get("updated_at") else datetime.utcnow(),
            "leave_taken": leave.get("leave_taken", 0),
            "remaining_leaves": leave.get("remaining_leaves", 20),
            "approved_by": leave.get("approved_by")
        }
        leaves.append(LeaveResponse(**leave_data))
    return leaves

# Approve/Reject leave (Admin only)
@router.put("/{leave_id}/status", response_model=LeaveResponse)
async def update_leave_status(
    leave_id: str,
    leave_update: LeaveUpdateStatus,
    current_admin: TokenPayload = Depends(require_admin)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        # Update leave_taken and remaining_leaves only if status changes to APPROVED
        update_data = {
            "status": leave_update.status,
            "approved_by": leave_update.approved_by,
            "updated_at": datetime.utcnow()
        }
        if leave_update.status == LeaveStatus.APPROVED and leave.get("status") != "approved":
            update_data["leave_taken"] = leave.get("leave_taken", 0) + leave.get("days", 0)
            update_data["remaining_leaves"] = max(0, leave.get("remaining_leaves", 20) - leave.get("days", 0))

        await leave_collection.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": update_data}
        )
        
        updated_leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        updated_data = {
            "_id": str(updated_leave["_id"]),
            "employee_id": updated_leave.get("employee_id", ""),
            "employee_name": updated_leave.get("employee_name", ""),
            "start_date": updated_leave.get("start_date").date() if updated_leave.get("start_date") else date.today(),
            "end_date": updated_leave.get("end_date").date() if updated_leave.get("end_date") else date.today(),
            "leave_type": updated_leave.get("leave_type", ""),
            "reason": updated_leave.get("reason", ""),
            "status": LeaveStatus(updated_leave.get("status", "pending")),
            "days": updated_leave.get("days", 0),
            "created_at": updated_leave.get("created_at") if updated_leave.get("created_at") else datetime.utcnow(),
            "updated_at": updated_leave.get("updated_at") if updated_leave.get("updated_at") else datetime.utcnow(),
            "leave_taken": updated_leave.get("leave_taken", 0),
            "remaining_leaves": updated_leave.get("remaining_leaves", 20),
            "approved_by": updated_leave.get("approved_by")
        }
        return LeaveResponse(**updated_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )