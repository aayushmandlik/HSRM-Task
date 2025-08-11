from fastapi import APIRouter, Depends, HTTPException
from schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeOut
from core.security import require_admin, get_current_user, TokenPayload
from services import employee_service
from typing import List

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.post("/create", response_model=EmployeeOut)
async def create_employee(data: EmployeeCreate, current_admin: TokenPayload = Depends(require_admin)):
    return await employee_service.create_employee(data)

@router.get("/getall", response_model=List[EmployeeOut])
async def get_all_employees(current_admin: TokenPayload = Depends(require_admin)):
    return await employee_service.get_all_employees()

@router.get("/{user_id}", response_model=EmployeeOut)
async def get_employee(user_id: str, current_user: TokenPayload = Depends(get_current_user)):
    return await employee_service.get_employee(user_id, current_user)

@router.put("/{emp_code}", response_model=EmployeeOut)
async def update_employee(emp_code: str, data: EmployeeUpdate, current_admin: TokenPayload = Depends(require_admin)):
    return await employee_service.update_employee(emp_code, data)

@router.delete("/{emp_code}", response_model=EmployeeOut)
async def delete_employee(emp_code: str, current_admin: TokenPayload = Depends(require_admin)):
    return await employee_service.delete_employee(emp_code)