from databases.database import users_collection

async def find_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

async def insert_user(user_dict: dict):
    result = await users_collection.insert_one(user_dict)
    return await users_collection.find_one({"_id": result.inserted_id})

async def find_all_users():
    return users_collection.find()