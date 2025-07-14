from fastapi import HTTPException,Depends,APIRouter
from databases.database import task_collection
from schemas.task_schema import TaskCreate,TaskUpdate,TaskOut,TaskComment
from core.security import require_admin,get_current_user,require_admin_or_user
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/tasks",tags={"Tasks"})


@router.post("/",response_model=TaskOut)
async def create_task(task: TaskCreate, current_admin: dict = Depends(require_admin)):
    task_data = task.dict()
    task_data["status"] = "Pending"
    task_data["created_at"] = datetime.utcnow()
    task_data["updated_at"] = datetime.utcnow()
    task_data["comment"] = []

    result = await task_collection.insert_one(task_data)
    task_data["id"] = str(result.inserted_id)
    return TaskOut(**task_data)

@router.get("/",response_model=List[TaskOut])
async def get_all_tasks(current_admin: dict = Depends(require_admin)):
    tasks = await task_collection.find().to_list(200)
    return [TaskOut(id=str(t["_id"]), **t) for t in tasks]


@router.get("/user/{user_id}",response_model=List[TaskOut])
async def get_user_tasks(user_id: str, current_user: dict = Depends(get_current_user)):
    tasks = await task_collection.find({"assigned_to":user_id}).to_list(length=100)
    return [TaskOut(id=str(t["_id"]), **t) for t in tasks]

@router.patch("/{task_id}/status",response_model=TaskOut)
async def update_task_status(task_id: str, update: TaskUpdate, current_user: dict = Depends(get_current_user)):
    result = await task_collection.find_one_and_update({"_id":ObjectId(task_id)},{"$set":{"status": update.status, "updated_at": datetime.utcnow()}},return_document=True)
    if not result:
        raise HTTPException(status_code=404,detail="Task Not found")
    return TaskOut(id=str(result["_id"]),**result)


@router.post("/{task_id}/comment",response_model=TaskOut)
async def add_comment(task_id: str, comment: TaskComment, user: dict = Depends(require_admin_or_user)):
    comment_data = {
        "user_id": comment.user_id,
        "message": comment.message,
        "timestamp": datetime.utcnow()
    }
    result = await task_collection.find_one_and_update({"_id":ObjectId(task_id)},{"$push": {"comments":comment_data},"$set":{"updated_at":datetime.utcnow()}},return_document=True)
    if not result:
        raise HTTPException(status_code=404,detail="Task Not Found")
    return TaskOut(id=str(result["_id"]), **result)


