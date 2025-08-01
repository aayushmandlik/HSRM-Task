from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime
from bson import ObjectId
from schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeOut
from core.security import require_admin,get_current_user, TokenPayload
from databases.database import employee_collection, users_collection, admins_collection

router = APIRouter(prefix="/employee", tags=['Employee'])

@router.post("/create", response_model=EmployeeOut)
async def create_employee(data: EmployeeCreate, current_admin: TokenPayload = Depends(require_admin)):
    user = await users_collection.find_one({"email": data.email})
    admin = await admins_collection.find_one({"email":data.email})
    if not user and not admin:
        raise HTTPException(status_code=400, detail="User with this email does not exist")
    
    existing = await employee_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")
    
    
    employee_dict = data.dict()
    if user:
        employee_dict["user_id"] = str(user["_id"]) if user and "_id" in user else None
    if admin:
        employee_dict["user_id"] = str(admin["_id"]) if admin and "_id" in admin else None
    result = await employee_collection.insert_one(employee_dict)
    employee_dict["_id"] = str(result.inserted_id)
    return employee_dict

@router.get("/getall", response_model=List[EmployeeOut])
async def get_all_employees(current_admin: TokenPayload = Depends(require_admin)):
    employees_cursor = employee_collection.find()
    employees = []
    async for emp in employees_cursor:
        emp["_id"] = str(emp["_id"])
        employees.append(emp)
    return employees

@router.get("/{user_id}", response_model=EmployeeOut)
async def get_employee(user_id: str, current_user: TokenPayload = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    emp = await employee_collection.find_one({"user_id": user_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp["_id"] = str(emp["_id"])
    return emp

@router.put("/{emp_code}", response_model=EmployeeOut)
async def update_employee(emp_code: str, data: EmployeeUpdate, current_admin: TokenPayload = Depends(require_admin)):
    result = await employee_collection.update_one({"emp_code": emp_code}, {"$set": data.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated = await employee_collection.find_one({"emp_code": emp_code})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated employee")
    updated["_id"] = str(updated["_id"])
    return updated

@router.delete("/{emp_code}", response_model=EmployeeOut)
async def delete_employee(emp_code: str, current_admin: TokenPayload = Depends(require_admin)):
    employee = await employee_collection.find_one({"emp_code": emp_code})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await employee_collection.delete_one({"emp_code": emp_code})
    employee["_id"] = str(employee["_id"])
    return employee