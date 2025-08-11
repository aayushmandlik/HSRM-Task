from datetime import date, datetime
from bson import ObjectId
from databases.database import leave_collection

async def find_all_leaves():
    return leave_collection.find()

async def find_pending_leaves():
    return leave_collection.find({"status": "pending"})

async def find_leave_by_id(leave_id: str):
    return await leave_collection.find_one({"_id": ObjectId(leave_id)})

async def update_leave(leave_id: str, update_data: dict):
    return await leave_collection.update_one(
        {"_id": ObjectId(leave_id)},
        {"$set": update_data}
    )
