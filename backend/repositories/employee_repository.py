from databases.database import employee_collection
from schemas.employee_schema import EmployeeUpdate
from fastapi import HTTPException
async def find_employee_by_email(email: str):
    return await employee_collection.find_one({"email": email})

async def insert_employee(employee_dict: dict):
    result = await employee_collection.insert_one(employee_dict)
    employee_dict["_id"] = str(result.inserted_id)
    return employee_dict

async def find_all_employees():
    return employee_collection.find()

async def find_employee_by_user_id(user_id: str):
    return await employee_collection.find_one({"user_id": user_id})

async def update_employee_by_code(emp_code: str, data: EmployeeUpdate):
    result = await employee_collection.update_one({"emp_code": emp_code}, {"$set": data.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated = await employee_collection.find_one({"emp_code": emp_code})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated employee")
    updated["_id"] = str(updated["_id"])
    return updated

async def delete_employee_by_code(emp_code: str):
    employee = await employee_collection.find_one({"emp_code": emp_code})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    await employee_collection.delete_one({"emp_code": emp_code})
    employee["_id"] = str(employee["_id"])
    return employee