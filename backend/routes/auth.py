from fastapi import APIRouter, HTTPException
from utils.db import db
from utils.security import hash_password, verify_password
from models.schemas import User
import uuid


router = APIRouter()
 
@router.post("/register")
async def register(user: User):
    hashed = hash_password(user.password)
    user_data = user.__dict__
    user_data["password"] = hashed
    user_data["user_id"] = str(uuid.uuid1())
    db.users.insert_one(user_data)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(body:dict):
    
    print(body)
    user =  db.users.find_one({"email": body["email"]})
    pass_verify =  verify_password(body["password"], user["password"])
    if not user or not pass_verify:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    data = {
        "user" : user["email"],
        "role" :user["role"],
        "user_id":user["user_id"]
        }
    print(data)
    return data
