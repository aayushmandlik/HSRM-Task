from datetime import date, datetime
from typing import List
from fastapi import HTTPException, status
from schemas.leave_schema import LeaveResponse, LeaveStatus
from services.leave_service import get_employee_leave_balance
from repositories.admin_leave_repository import (
    find_all_leaves, find_pending_leaves, find_leave_by_id, update_leave
)

async def get_all_leave_requests():
    leaves_cursor = await find_all_leaves()
    return await process_leave_cursor(leaves_cursor)

async def fetch_pending_leave_requests():
    leaves_cursor = await find_pending_leaves()
    return await process_leave_cursor(leaves_cursor)

async def process_leave_cursor(leaves_cursor):
    leaves = []
    async for leave in leaves_cursor:
        leave_type = leave.get("leave_type", "Unknown")
        if leave_type not in ["Medical", "Casual", "Annual", "Unknown"]:
            leave_type = "Unknown"
        employee_id = leave.get("employee_id", "")
        if not employee_id:
            continue
        leave_balances = await get_employee_leave_balance(employee_id)
        leaves.append(LeaveResponse(
            _id=str(leave["_id"]),
            employee_id=employee_id,
            employee_name=leave.get("employee_name", "Unknown Employee"),
            start_date=leave.get("start_date").date() if leave.get("start_date") else date.today(),
            end_date=leave.get("end_date").date() if leave.get("end_date") else date.today(),
            leave_type=leave_type,
            reason=leave.get("reason", ""),
            status=LeaveStatus(leave.get("status", "pending")),
            days=leave.get("days", 0),
            created_at=leave.get("created_at") if leave.get("created_at") else datetime.utcnow(),
            updated_at=leave.get("updated_at") if leave.get("updated_at") else datetime.utcnow(),
            leave_balances=leave_balances,
            approved_by=leave.get("approved_by")
        ))
    return leaves

async def update_leave_status_service(leave_id: str, leave_update):
    leave = await find_leave_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    leave_type = leave.get("leave_type", "Unknown")
    if leave_type not in ["Medical", "Casual", "Annual"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid leave type: {leave_type}. Must be Medical, Casual, or Annual"
        )

    employee_id = leave.get("employee_id", "")
    if not employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID is missing in leave record")

    update_data = {
        "status": leave_update.status,
        "approved_by": leave_update.approved_by,
        "updated_at": datetime.utcnow()
    }

    if leave_update.status == LeaveStatus.APPROVED and leave.get("status") != "approved":
        _, remaining_leaves = await get_employee_leave_balance(employee_id, leave_type)
        if remaining_leaves < leave.get("days", 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient {leave_type} leave balance. Remaining: {remaining_leaves} days, Requested: {leave.get('days', 0)} days"
            )
        leave_balances = await get_employee_leave_balance(employee_id)
        leave_balances[leave_type] = max(0, leave_balances[leave_type] - leave.get("days", 0))
        update_data["leave_balances"] = leave_balances

    await update_leave(leave_id, update_data)

    updated_leave = await find_leave_by_id(leave_id)
    updated_leave_balances = await get_employee_leave_balance(updated_leave.get("employee_id", ""))

    return LeaveResponse(
        _id=str(updated_leave["_id"]),
        employee_id=updated_leave.get("employee_id", ""),
        employee_name=updated_leave.get("employee_name", "Unknown Employee"),
        start_date=updated_leave.get("start_date").date() if updated_leave.get("start_date") else date.today(),
        end_date=updated_leave.get("end_date").date() if updated_leave.get("end_date") else date.today(),
        leave_type=updated_leave.get("leave_type", "Unknown"),
        reason=updated_leave.get("reason", ""),
        status=LeaveStatus(updated_leave.get("status", "pending")),
        days=updated_leave.get("days", 0),
        created_at=updated_leave.get("created_at") if updated_leave.get("created_at") else datetime.utcnow(),
        updated_at=updated_leave.get("updated_at") if updated_leave.get("updated_at") else datetime.utcnow(),
        leave_balances=updated_leave_balances,
        approved_by=updated_leave.get("approved_by")
    )