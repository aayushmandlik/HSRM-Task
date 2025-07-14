from fastapi import APIRouter,HTTPException,Depends,status
from schemas.employee_schema import EmployeeCreate,EmployeeUpdate,EmployeeOut
from bson import ObjectId
from typing import List
from core.security import get_current_user,verify_token,require_admin
from databases.database import employee_collection

router = APIRouter(prefix="/employee",tags=['Employee'])

@router.post("/",response_model=EmployeeOut)
async def create_employee(data: EmployeeCreate, current_admin:dict = Depends(require_admin)):
    existing = await employee_collection.find_one({"user_id":data.user_id})
    if existing:
        raise HTTPException(status_code=400,detail="Employee Already Exits")
    employee_dict = data.dict()
    employee_dict["status"] = "Active"
    result = await employee_collection.insert_one(employee_dict)
    employee_dict["__id"] = str(result.inserted_id)
    return employee_dict

@router.get("/",response_model=List[EmployeeOut])
async def get_all_employees(current_admin: dict = Depends(require_admin)):
    employees_cursor = employee_collection.find()
    employees = []
    async for emp in employees_cursor:
        emp["_id"] = str(emp["_id"])
        employees.append(emp)
    return employees

@router.get("/{user_id}",response_model=EmployeeOut)
async def get_employee(user_id: str, token_payload: dict = Depends(verify_token)):
    if token_payload.get("role")!="admin" and token_payload.get("sub")!=user_id:
        raise HTTPException(status_code=403,detail="Not Authorized")
    emp = await employee_collection.find_one({"user_id": user_id})
    if not emp:
        raise HTTPException(status_code=404,detail="Employee Not Found")
    emp["_id"] = str(emp["_id"])
    return emp

@router.put("/{user_id}",response_model=EmployeeOut)
async def update_employee(user_id: str, data: EmployeeUpdate, current_admin: dict = Depends(require_admin)):
    print("userId: ",user_id)
    result = await employee_collection.update_one({"user_id":user_id},{"$set":data.dict(exclude_unset=True)})
    if result.matched_count==0:
        raise HTTPException(status_code=404,detail="Employee not found")
    updated = await employee_collection.find_one({"user_id":user_id})
    updated["_id"] = str(updated["_id"])
    return updated

@router.get("/manager/{manager_id}",response_model=List[EmployeeOut])
async def get_employees_by_manager(manager_id: str, current_admin: dict = Depends(require_admin)):
    cursor = employee_collection.find({"reporting_manager_id":manager_id})
    employees = []
    async for emp in cursor:
        emp["_id"] = str(emp["_id"])
        employees.append(emp)
    return employees

@router.delete("/{user_id}", response_model=EmployeeOut)
async def delete_employee(user_id: str, current_admin: dict = Depends(require_admin)):
    print("userid: ",user_id)
    employee = await employee_collection.find_one({"user_id": user_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee Not Found")

    await employee_collection.delete_one({"user_id": user_id})
    employee["_id"] = str(employee["_id"])
    return employee  
