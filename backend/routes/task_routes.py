from fastapi import APIRouter, Depends, HTTPException
from typing import List
from core.security import require_admin, get_current_user
from schemas.task_schema import TaskCreate, TaskUpdate, TaskOut, TaskUpdateStatus
from services import task_service as ts

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskOut)
async def create_task(task: TaskCreate, current_admin: dict = Depends(require_admin)):
    data = await ts.create_task_service(task, current_admin)
    return TaskOut(**data)

@router.get("/", response_model=List[TaskOut])
async def get_all_tasks(current_admin: dict = Depends(require_admin)):
    tasks = await ts.get_all_tasks_service()
    return [
        TaskOut(
            id=str(t["_id"]),
            title=t["title"],
            description=t["description"],
            assigned_to=await ts.get_names_from_user_ids(t["assigned_to"]),
            assigned_by=t["assigned_by"],
            status=t["status"],
            priority=t["priority"],
            due_date=t["due_date"],
            created_at=t["created_at"],
            updated_at=t["updated_at"],
            comments=t.get("comments", []),
            project=t.get("project")
        )
        for t in tasks
    ]

@router.get("/mytasks", response_model=List[TaskOut])
async def get_my_tasks(current_user: dict = Depends(get_current_user)):
    tasks = await ts.get_my_task_service(current_user["user_id"])
    return [
        TaskOut(
            id=str(t["_id"]),
            title=t["title"],
            description=t["description"],
            assigned_to=await ts.get_names_from_user_ids(t["assigned_to"]),
            assigned_by=t["assigned_by"],
            status=t["status"],
            priority=t["priority"],
            due_date=t["due_date"],
            created_at=t["created_at"],
            updated_at=t["updated_at"],
            comments=t.get("comments", []),
            project=t.get("project")
        )
        for t in tasks
    ]

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, task: TaskUpdate, current_admin: dict = Depends(require_admin)):
    updated = await ts.update_task_service(task_id, task)
    return TaskOut(id=str(updated["_id"]), **updated)

@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(task_id: str, update: TaskUpdateStatus, current_user: dict = Depends(get_current_user)):
    updated = await ts.update_task_status_service(task_id, current_user["user_id"], update.status)
    return TaskOut(id=str(updated["_id"]), **updated)

@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(require_admin)):
    return await ts.delete_task_service(task_id)

