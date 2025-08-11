from databases.database import task_collection,employee_collection
from bson import ObjectId

async def create_task(task_data: dict):
    result = await task_collection.insert_one(task_data)
    return str(result.inserted_id)

async def update_task_by_id(task_id: str, update_data: dict):
    return await task_collection.find_one_and_update({"_id":ObjectId(task_id)},{"$set":update_data},return_document=True)

async def delete_task_by_id(task_id: str):
    return await task_collection.delete_one({"_id":ObjectId(task_id)})

async def find_all_tasks():
    return await task_collection.find().to_list(200)

async def find_task_by_id(task_id: str):
    return await task_collection.find_one({"_id":ObjectId(task_id)})

async def find_tasks_by_user_id(user_id: str):
    return await task_collection.find({"assigned_to": {"$in":[user_id]}}).to_list(100)

async def find_employee_by_name(name:str):
    return await employee_collection.find_one({"name":name.strip()})

async def find_employee_by_user_id(user_ids: list):
    return await employee_collection.find({"user_id": {"$in":user_ids}}).to_list(length=len(user_ids))


