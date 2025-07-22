from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from schemas.leave_schema import LeaveCreate, LeaveResponse, LeaveUpdate,LeaveUpdateStatus, LeaveStatus
from databases.database import leave_collection, employee_collection, users_collection 
from core.security import require_admin, require_admin_or_user, TokenPayload
from datetime import date
from datetime import datetime

router = APIRouter(prefix="/Emp_leave", tags=["Employee Leave"])

def calculate_leave_days(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1

async def get_employee_leave_balance(employee_id: str) -> tuple[int, int]:
    cursor = leave_collection.find({
        "employee_id": employee_id,
        "status": LeaveStatus.APPROVED
    })
    days_list = [leave["days"] async for leave in cursor]
    approved_leaves = len(days_list)
    total_days_taken = sum(days_list) if days_list else 0
    remaining_leaves = 20 - total_days_taken
    return total_days_taken, max(0, remaining_leaves)

@router.post("/request", response_model=LeaveResponse)
async def request_leave(
    leave: LeaveCreate,
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    if leave.start_date > leave.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    days = calculate_leave_days(leave.start_date, leave.end_date)
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date range"
        )

    # Check remaining leaves
    _, remaining_leaves = await get_employee_leave_balance(current_user.user_id)
    if remaining_leaves < days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient leave balance. Remaining: {remaining_leaves} days, Requested: {days} days"
        )

    # Fetch employee name (assuming it's in users_collection)
    emp = await employee_collection.find_one({"user_id": current_user.user_id})
    employee_name = emp.get("name", "Unknown Employee") if emp else "Unknown Employee"

    leave_dict = leave.dict()
    leave_dict["start_date"] = datetime.combine(leave.start_date, datetime.min.time())
    leave_dict["end_date"] = datetime.combine(leave.end_date, datetime.min.time())
    leave_dict.update({
        "employee_id": current_user.user_id,
        "employee_name": employee_name,
        "status": LeaveStatus.PENDING,
        "days": days,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "leave_taken": 0,
        "remaining_leaves": remaining_leaves,
        "approved_by": None
    })
    
    result = await leave_collection.insert_one(leave_dict)
    leave_dict["_id"] = str(result.inserted_id)
    return leave_dict

@router.patch("/{leave_id}", response_model=LeaveResponse)
async def update_leave(
    leave_id: str,
    update: LeaveUpdate,
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        if leave["employee_id"] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this leave request"
            )

        if leave["status"] != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be updated"
            )

        update_data = update.dict(exclude_unset=True)
        if "start_date" in update_data or "end_date" in update_data:
            start_date = update_data.get("start_date", leave["start_date"].date())
            end_date = update_data.get("end_date", leave["end_date"].date())
            if start_date > end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date"
                )
            days = calculate_leave_days(start_date, end_date)
            if days <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date range"
                )
            _, remaining_leaves = await get_employee_leave_balance(current_user.user_id)
            if remaining_leaves + leave["days"] - days < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient leave balance. Remaining: {remaining_leaves} days, Adjusted Request: {days} days"
                )
            update_data["days"] = days
            update_data["start_date"] = datetime.combine(start_date, datetime.min.time())
            update_data["end_date"] = datetime.combine(end_date, datetime.min.time())

        update_data["updated_at"] = datetime.utcnow()
        updated = await leave_collection.find_one_and_update(
            {"_id": ObjectId(leave_id)},
            {"$set": update_data},
            return_document=True
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        updated["_id"] = str(updated["_id"])
        return updated
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )

@router.delete("/{leave_id}")
async def delete_leave(
    leave_id: str,
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        if leave["employee_id"] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this leave request"
            )

        if leave["status"] != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be deleted"
            )

        result = await leave_collection.delete_one({"_id": ObjectId(leave_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        return {"message": "Leave request deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )

@router.patch("/{leave_id}/status", response_model=LeaveResponse)
async def update_leave_status(
    leave_id: str,
    update: LeaveUpdateStatus,
    current_user: TokenPayload = Depends(require_admin)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        if update.status == LeaveStatus.APPROVED and leave["status"] != LeaveStatus.APPROVED:
            leave_taken, remaining_leaves = await get_employee_leave_balance(leave["employee_id"])
            if remaining_leaves < leave["days"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient leave balance. Remaining: {remaining_leaves} days, Required: {leave['days']} days"
                )
            leave_taken += leave["days"]
            remaining_leaves = 20 - leave_taken

        updated = await leave_collection.find_one_and_update(
            {"_id": ObjectId(leave_id)},
            {
                "$set": {
                    "status": update.status,
                    "updated_at": datetime.utcnow(),
                    "approved_by": current_user.email if update.status == LeaveStatus.APPROVED else leave.get("approved_by")
                }
            },
            return_document=True
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        await leave_collection.update_many(
            {"employee_id": updated["employee_id"]},
            {
                "$set": {
                    "leave_taken": leave_taken,
                    "remaining_leaves": remaining_leaves
                }
            }
        )

        updated["_id"] = str(updated["_id"])
        return updated
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )

@router.get("/my-requests", response_model=List[LeaveResponse])
async def get_my_leave_requests(
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    leaves_cursor = leave_collection.find({"employee_id": current_user.user_id})
    leaves = []
    async for leave in leaves_cursor:
        leave["_id"] = str(leave["_id"])
        leaves.append(leave)
    return leaves

@router.get("/{leave_id}", response_model=LeaveResponse)
async def get_leave_details(
    leave_id: str,
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        if current_user.role != "admin" and leave["employee_id"] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this leave request"
            )
        
        leave["_id"] = str(leave["_id"])
        return leave
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )