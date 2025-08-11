from databases.database import attendance_collection, employee_collection
from datetime import datetime, timedelta

async def get_attendance_logs_by_date(date=None):
    query = {}
    if date:
        filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        query["check_in"] = {
            "$gte": datetime(filter_date.year, filter_date.month, filter_date.day),
            "$lt": datetime(filter_date.year, filter_date.month, filter_date.day) + timedelta(days=1)
        }
    return await attendance_collection.find(query).to_list(length=1000)

async def get_all_employees():
    return await employee_collection.find().to_list(length=1000)
