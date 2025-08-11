from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime,time
from schemas.leave_schema import LeaveCreate, LeaveUpdate, LeaveStatus
from repositories import leave_repository, employee_repository

async def calculate_leave_days(start_date, end_date):
    return (end_date - start_date).days + 1

async def get_employee_leave_balance(employee_id: str, leave_type: str = None):
    return await leave_repository.calculate_balance(employee_id, leave_type)

async def request_leave(leave: LeaveCreate, current_user):
    if leave.start_date > leave.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    days = await calculate_leave_days(leave.start_date, leave.end_date)
    if leave.leave_type not in ["Medical", "Casual", "Annual"]:
        raise HTTPException(status_code=400, detail="Invalid leave type")

    _, remaining_leaves = await get_employee_leave_balance(current_user.user_id, leave.leave_type)
    if remaining_leaves < days:
        raise HTTPException(status_code=400, detail=f"Insufficient {leave.leave_type} balance")

    emp = await employee_repository.find_employee_by_user_id(current_user.user_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    leave_dict = leave.dict()
    leave_dict.update({
        "employee_id": current_user.user_id,
        "employee_name": emp.get("name", "Unknown"),
        "start_date": datetime.combine(leave.start_date,time.min),
        "end_date":datetime.combine(leave.end_date,time.min),
        "status": LeaveStatus.PENDING,
        "days": days,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "leave_balances": await get_employee_leave_balance(current_user.user_id),
        "approved_by": None
    })
    return await leave_repository.insert_leave(leave_dict)

async def get_my_leave_requests(current_user):
    return await leave_repository.get_user_leaves(current_user.user_id)

async def update_leave_request(leave_id: str, update_data: LeaveUpdate, current_user):
    return await leave_repository.update_leave(leave_id, update_data, current_user)

async def delete_leave_request(leave_id: str, current_user):
    return await leave_repository.delete_leave(leave_id, current_user)