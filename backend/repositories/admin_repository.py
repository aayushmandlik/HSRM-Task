from databases.database import admins_collection

async def find_admin_by_email(email: str):
    return await admins_collection.find_one({"email": email})

async def insert_admin(admin_dict: dict):
    return await admins_collection.insert_one(admin_dict)

async def find_all_admins():
    return admins_collection.find()