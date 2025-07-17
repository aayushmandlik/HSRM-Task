from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from bson import ObjectId
from schemas.leave_schema import LeaveCreate, LeaveResponse, LeaveUpdate, LeaveStatus
from databases.database import leave_collection
from core.security import require_admin, require_admin_or_user, TokenPayload
from datetime import date

router = APIRouter(prefix="/Emp_leave", tags=["Employee Leave"])




def calculate_leave_days(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1

# Create leave request
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

    leave_dict = leave.dict()
    leave_dict["start_date"] = datetime.combine(leave.start_date, datetime.min.time())
    leave_dict["end_date"] = datetime.combine(leave.end_date, datetime.min.time())
    leave_dict.update({
        "employee_id": current_user.user_id,
        "status": LeaveStatus.PENDING,
        "days": days,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    result = await leave_collection.insert_one(leave_dict)
    leave_dict["_id"] = str(result.inserted_id)
    return leave_dict


# Get employee's own leave requests
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



# Get specific leave request details
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