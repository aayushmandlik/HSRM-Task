from fastapi import HTTPException, Depends, APIRouter
from databases.database import task_collection, employee_collection
from schemas.task_schema import TaskCreate, TaskUpdate, TaskOut, TaskUpdateStatus
from core.security import require_admin, get_current_user
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/tasks", tags={"Tasks"})

@router.post("/", response_model=TaskOut)
async def create_task(task: TaskCreate, current_admin: dict = Depends(require_admin)):
    
    assigned_user_ids = []
    for name in task.assigned_to_emails:
        emp = await employee_collection.find_one({"name": name.strip()})
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee not found for name: {name}")
        assigned_user_ids.append(emp["user_id"])  

    task_data = {
        "title": task.title,
        "description": task.description,
        "priority": task.priority or "Normal",
        "due_date": task.due_date,
        "status": task.status or "Pending",
        "assigned_to": assigned_user_ids, 
        "assigned_by": task.assigned_by or current_admin.name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "comments": [],
        "project": task.project
    }

    result = await task_collection.insert_one(task_data)
    task_data["id"] = str(result.inserted_id)
    return TaskOut(**task_data)

@router.get("/", response_model=List[TaskOut])
async def get_all_tasks(current_admin: dict = Depends(require_admin)):
    tasks = await task_collection.find().to_list(200)
    return [
        TaskOut(
            id=str(t["_id"]),
            title=t.get("title", ""),
            description=t.get("description", ""),
            assigned_to=await get_names_from_user_ids(t.get("assigned_to", [])),  
            assigned_by=t.get("assigned_by", ""),
            status=t.get("status", "Pending"),
            priority=t.get("priority", "Normal"),
            due_date=t.get("due_date"),
            created_at=t.get("created_at", datetime.utcnow()),
            updated_at=t.get("updated_at", datetime.utcnow()),
            comments=t.get("comments", []),
            project=t.get("project", None)
        )
        for t in tasks
    ]

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, task: TaskUpdate, current_admin: dict = Depends(require_admin)):
    existing_task = await task_collection.find_one({"_id": ObjectId(task_id)})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = {"updated_at": datetime.utcnow()}
    if task.title is not None:
        update_data["title"] = task.title
    if task.description is not None:
        update_data["description"] = task.description
    if task.assigned_to_emails is not None:
        if not isinstance(task.assigned_to_emails, list):
            raise HTTPException(status_code=400, detail="assigned_to_emails must be a list")
        assigned_user_ids = []
        for name in task.assigned_to_emails:
            emp = await employee_collection.find_one({"name": name.strip()})
            if not emp:
                raise HTTPException(status_code=404, detail=f"Employee not found for name: {name}")
            assigned_user_ids.append(emp["user_id"])  
        update_data["assigned_to"] = assigned_user_ids
    if task.assigned_by is not None:
        update_data["assigned_by"] = task.assigned_by
    if task.priority is not None:
        update_data["priority"] = task.priority
    if task.due_date is not None:
        update_data["due_date"] = task.due_date
    if task.status is not None:
        update_data["status"] = task.status
    if task.project is not None:
        update_data["project"] = task.project

    updated = await task_collection.find_one_and_update(
        {"_id": ObjectId(task_id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update task")
    return TaskOut(id=str(updated["_id"]), **updated)

@router.get("/mytasks", response_model=List[TaskOut])
async def get_my_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"] 
    tasks = await task_collection.find({"assigned_to": {"$in": [user_id]}}).to_list(length=100)
    return [
        TaskOut(
            id=str(t["_id"]),
            title=t.get("title", ""),
            description=t.get("description", ""),
            assigned_to=await get_names_from_user_ids(t.get("assigned_to", [])),  
            assigned_by=t.get("assigned_by", ""),
            status=t.get("status", "Pending"),
            priority=t.get("priority", "Normal"),
            due_date=t.get("due_date"),
            created_at=t.get("created_at", datetime.utcnow()),
            updated_at=t.get("updated_at", datetime.utcnow()),
            comments=t.get("comments", []),
            project=t.get("project", None)
        )
        for t in tasks
    ]

@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(task_id: str, update: TaskUpdateStatus, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]  
    task = await task_collection.find_one({"_id": ObjectId(task_id)})

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if str(user_id) not in task.get("assigned_to", []):  
        raise HTTPException(status_code=403, detail="Not allowed to update this task")

    updated = await task_collection.find_one_and_update(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}},
        return_document=True
    )
    return TaskOut(id=str(updated["_id"]), **updated)

@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(require_admin)):
    task = await task_collection.find_one({"_id": ObjectId(task_id)})

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await task_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete task")
    return {"message": "Task deleted successfully"}

async def get_names_from_user_ids(user_ids: list) -> list:
    if not user_ids:
        return []
    employees = await employee_collection.find({"user_id": {"$in": user_ids}}).to_list(length=len(user_ids))
    name_map = {str(emp["user_id"]): emp["name"] for emp in employees}
    return [name_map.get(str(uid), str(uid)) for uid in user_ids]