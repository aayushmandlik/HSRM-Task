from databases.database import leave_collection
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from schemas.leave_schema import LeaveStatus

async def calculate_balance(employee_id: str, leave_type: str = None):
    initial_balance = {"Medical": 10, "Casual": 10, "Annual": 10}
    if leave_type:
        cursor = leave_collection.find({"employee_id": employee_id, "status": LeaveStatus.APPROVED, "leave_type": leave_type})
        days = [doc["days"] async for doc in cursor]
        total = sum(days)
        return total, max(0, initial_balance[leave_type] - total)
    else:
        balances = {}
        for lt in ["Medical", "Casual", "Annual"]:
            cursor = leave_collection.find({"employee_id": employee_id, "status": LeaveStatus.APPROVED, "leave_type": lt})
            days = [doc["days"] async for doc in cursor]
            balances[lt] = max(0, initial_balance[lt] - sum(days))
        return balances

async def insert_leave(data):
    result = await leave_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data

async def get_user_leaves(employee_id):
    cursor = leave_collection.find({"employee_id": employee_id})
    leaves = []
    async for leave in cursor:
        leave["_id"] = str(leave["_id"])
        leave["leave_balances"] = await calculate_balance(employee_id)
        leaves.append(leave)
    return leaves

async def update_leave(leave_id, update_data, user):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(status_code=404, detail="Leave not found")
        if leave["employee_id"] != user.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if leave["status"] != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending requests can be updated")

        update_fields = {}
        if update_data.start_date and update_data.end_date:
            if update_data.start_date > update_data.end_date:
                raise HTTPException(status_code=400, detail="Invalid date range")
            days = (update_data.end_date - update_data.start_date).days + 1
            _, remaining = await calculate_balance(user.user_id, update_data.leave_type or leave["leave_type"])
            if remaining < days:
                raise HTTPException(status_code=400, detail="Insufficient leave balance")
            update_fields.update({
                "start_date": datetime.combine(update_data.start_date, datetime.min.time()),
                "end_date": datetime.combine(update_data.end_date, datetime.min.time()),
                "days": days
            })
        if update_data.reason:
            update_fields["reason"] = update_data.reason
        if update_data.leave_type:
            update_fields["leave_type"] = update_data.leave_type

        update_fields["updated_at"] = datetime.utcnow()
        update_fields["leave_balances"] = await calculate_balance(user.user_id)

        await leave_collection.update_one({"_id": ObjectId(leave_id)}, {"$set": update_fields})
        updated = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        updated["_id"] = str(updated["_id"])
        return updated

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid leave ID")

async def delete_leave(leave_id, user):
    try:
        leave = await leave_collection.find_one({"_id": ObjectId(leave_id)})
        if not leave:
            raise HTTPException(status_code=404, detail="Leave not found")
        if leave["employee_id"] != user.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if leave["status"] != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending can be deleted")
        await leave_collection.delete_one({"_id": ObjectId(leave_id)})
        leave["_id"] = str(leave["_id"])
        return leave
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid leave ID")