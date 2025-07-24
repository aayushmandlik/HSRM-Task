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


    _, remaining_leaves = await get_employee_leave_balance(current_user.user_id)
    if remaining_leaves < days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient leave balance. Remaining: {remaining_leaves} days, Requested: {days} days"
        )


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