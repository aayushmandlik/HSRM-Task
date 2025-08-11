from fastapi import HTTPException
from core.security import TokenPayload
from schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from repositories import employee_repository, user_repository, admin_repository

async def create_employee(data: EmployeeCreate):
    user = await user_repository.find_user_by_email(data.email)
    admin = await admin_repository.find_admin_by_email(data.email)
    if not user and not admin:
        raise HTTPException(status_code=400, detail="User with this email does not exist")

    existing = await employee_repository.find_employee_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    employee_dict = data.dict()
    if user:
        employee_dict["user_id"] = str(user["_id"])
    elif admin:
        employee_dict["user_id"] = str(admin["_id"])

    result = await employee_repository.insert_employee(employee_dict)
    return result

async def get_all_employees():
    employees_cursor = await employee_repository.find_all_employees()
    employees = []
    async for emp in employees_cursor:
        emp["_id"] = str(emp["_id"])
        employees.append(emp)
    return employees

async def get_employee(user_id: str, current_user: TokenPayload):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    emp = await employee_repository.find_employee_by_user_id(user_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp["_id"] = str(emp["_id"])
    return emp

async def update_employee(emp_code: str, data: EmployeeUpdate):
    updated = await employee_repository.update_employee_by_code(emp_code, data)
    return updated

async def delete_employee(emp_code: str):
    deleted = await employee_repository.delete_employee_by_code(emp_code)
    return deleted