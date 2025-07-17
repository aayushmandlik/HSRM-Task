from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import datetime, date
from bson import ObjectId
from schemas.payroll_schema import PayrollCreate, PayrollResponse, PayrollUpdate
from databases.database import payroll_collection, employee_collection
from core.security import require_admin, require_admin_or_user, TokenPayload

router = APIRouter(prefix="/payroll", tags=["Payroll"])

# Create payroll record (Admin only)
@router.post("/", response_model=PayrollResponse)
async def create_payroll(
    payroll: PayrollCreate,
    current_admin: TokenPayload = Depends(require_admin)
):
    # Verify employee exists
    employee = await employee_collection.find_one({"emp_code": payroll.employee_id,"email":payroll.email})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Calculate net salary
    net_salary = payroll.basic_salary + payroll.bonus - payroll.deductions

    # Convert dates to datetime for MongoDB compatibility
    payroll_dict = payroll.dict()
    payroll_dict["pay_period_start"] = datetime.combine(payroll.pay_period_start, datetime.min.time())
    payroll_dict["pay_period_end"] = datetime.combine(payroll.pay_period_end, datetime.min.time())
    payroll_dict.update({
        "net_salary": net_salary,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    result = await payroll_collection.insert_one(payroll_dict)
    payroll_dict["_id"] = str(result.inserted_id)
    return payroll_dict

# Get all payroll records (Admin only)
@router.get("/", response_model=List[PayrollResponse])
async def get_all_payrolls(
    current_admin: TokenPayload = Depends(require_admin)
):
    payrolls_cursor = payroll_collection.find()
    payrolls = []
    async for payroll in payrolls_cursor:
        payroll["_id"] = str(payroll["_id"])
        payrolls.append(payroll)
    return payrolls

# Get employee's own payroll records
@router.get("/my-payrolls", response_model=List[PayrollResponse])
async def get_my_payrolls(
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    # Verify employee exists for this user
    employee = await employee_collection.find_one({"user_id": current_user.user_id})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found for this user"
        )
    
    payrolls_cursor = payroll_collection.find({"employee_id": current_user.user_id})
    payrolls = []
    async for payroll in payrolls_cursor:
        payroll["_id"] = str(payroll["_id"])
        payrolls.append(payroll)
    return payrolls

# Get specific payroll record
@router.get("/{payroll_id}", response_model=PayrollResponse)
async def get_payroll_details(
    payroll_id: str,
    current_user: TokenPayload = Depends(require_admin_or_user)
):
    try:
        payroll = await payroll_collection.find_one({"_id": ObjectId(payroll_id)})
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll record not found"
            )
        
        # Verify employee exists for this user if not admin
        if current_user.role != "admin":
            employee = await employee_collection.find_one({"user_id": current_user.user_id})
            if not employee or payroll["employee_id"] != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this payroll record"
                )
        
        payroll["_id"] = str(payroll["_id"])
        return payroll
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payroll ID format"
        )

# Update payroll record (Admin only)
@router.put("/{payroll_id}", response_model=PayrollResponse)
async def update_payroll(
    payroll_id: str,
    payroll_update: PayrollUpdate,
    current_admin: TokenPayload = Depends(require_admin)
):
    try:
        payroll = await payroll_collection.find_one({"_id": ObjectId(payroll_id)})
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll record not found"
            )
        
        update_data = payroll_update.dict(exclude_unset=True)
        if "basic_salary" in update_data or "bonus" in update_data or "deductions" in update_data:
            basic_salary = update_data.get("basic_salary", payroll["basic_salary"])
            bonus = update_data.get("bonus", payroll["bonus"])
            deductions = update_data.get("deductions", payroll["deductions"])
            update_data["net_salary"] = basic_salary + bonus - deductions
        
        if "pay_period_start" in update_data:
            update_data["pay_period_start"] = datetime.combine(payroll_update.pay_period_start, datetime.min.time())
        if "pay_period_end" in update_data:
            update_data["pay_period_end"] = datetime.combine(payroll_update.pay_period_end, datetime.min.time())
        
        update_data["updated_at"] = datetime.utcnow()
        await payroll_collection.update_one(
            {"_id": ObjectId(payroll_id)},
            {"$set": update_data}
        )
        
        updated_payroll = await payroll_collection.find_one({"_id": ObjectId(payroll_id)})
        updated_payroll["_id"] = str(updated_payroll["_id"])
        return updated_payroll
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payroll ID format"
        )

# Delete payroll record (Admin only)
@router.delete("/{payroll_id}", response_model=PayrollResponse)
async def delete_payroll(
    payroll_id: str,
    current_admin: TokenPayload = Depends(require_admin)
):
    try:
        payroll = await payroll_collection.find_one({"_id": ObjectId(payroll_id)})
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll record not found"
            )
        
        await payroll_collection.delete_one({"_id": ObjectId(payroll_id)})
        payroll["_id"] = str(payroll["_id"])
        return payroll
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payroll ID format"
        )