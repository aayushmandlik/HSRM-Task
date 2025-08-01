from repositories import task_repository as tr
from datetime import datetime
from fastapi import HTTPException,Depends
from schemas.task_schema import TaskCreate,TaskUpdate,TaskUpdateStatus,TaskOut
from core.security import require_admin,get_current_user
from typing import List

async def create_task_service(task: TaskCreate,current_admin: dict):
    assigned_user_ids = []
    for name in task.assigned_to:
        emp = await tr.find_employee_by_name(name)
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

    task_id = await tr.create_task(task_data)
    task_data["id"] = task_id
    return task_data

async def update_task_service(task_id:str,task:TaskUpdate,current_admin: dict):
    existing = await tr.find_task_by_id(task_id)
    if not existing:
        raise HTTPException(status_code=404,detail="Task Not Found")
    
    update_data = {"updated_at": datetime.utcnow()}
    if task.title is not None:
        update_data["title"] = task.title
    if task.description is not None:
        update_data["description"] = task.description
    if task.assigned_to is not None:
        if not isinstance(task.assigned_to, list):
            raise HTTPException(status_code=400, detail="assigned_to must be a list")
        assigned_user_ids = []
        for name in task.assigned_to:
            emp = await tr.find_employee_by_name(name)
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

    updated = await tr.update_task_by_id(task_id,update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update task")
    return updated


async def delete_task_service(task_id,current_admin:dict):
    task = await tr.find_task_by_id(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await tr.delete_task_by_id(task_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete task")
    return {"message": "Task deleted successfully"}

async def get_all_tasks_service():
    return await tr.find_all_tasks()

async def get_my_task_service(user_id: str):
    return await tr.find_tasks_by_user_id(user_id)

async def update_task_status_service(task_id: str, user_id:str, status: str):
    task = await tr.find_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")
    if user_id not in task.get("assigned_to",[]):
        raise HTTPException(status_code=403,detail="Not allowed to update this task")
    return await tr.update_task_by_id(task_id,{
        "status": status,
        "updated_at": datetime.utcnow()
    })

async def get_names_from_user_ids(user_ids: list) -> List:
    employees  = await tr.find_employee_by_user_id(user_ids)
    name_map = {str(emp["user_id"]): emp["name"] for emp in employees}
    return [name_map.get(str(uid),str(uid)) for uid in user_ids]
