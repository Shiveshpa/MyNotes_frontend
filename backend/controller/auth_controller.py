from fastapi import FastAPI, Depends, HTTPException, status, Cookie
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.responses import JSONResponse
import os 
from fastapi import APIRouter,Header
from utils.verifyUser import verify_token
from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()


# Replace with your secret key

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# MongoDB setup
# client = AsyncIOMotorClient("mongodb://localhost:27017")
# db = client.notes
load_dotenv()

# Retrieve the MongoDB URI from environment variables
mongodb_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB using the URI
client = AsyncIOMotorClient(mongodb_uri)
db = client.notes

# Bcrypt password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
router = APIRouter()
# Models for request/response
class User(BaseModel):
    username: str
    email: EmailStr
    password: str

class SigninUser(BaseModel):
    email: EmailStr
    password: str

# JWT Token creation function
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Utility to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Utility to hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# Signup Route
@router.post("/signup")
async def signup(user: User):
    # Check if user already exists
    print(user)
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash the password
    hashed_password = hash_password(user.password)
    print(hashed_password)
    
    # Create new user document
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    }
    # Save user to database
    await db.users.insert_one(new_user)
    print("saved")

    return {"success": True, "message": "User Created Successfully"}

# Signin Route
@router.post("/signin")
async def signin(user: SigninUser):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify password
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Wrong credentials")

    # Create JWT token
    print(existing_user["_id"])
    token = create_jwt_token({"id": str(existing_user["_id"])})
    
    # Create response and set cookie
    response = JSONResponse({"success": True, "message": "Login Successful!", "token": token})
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="None", secure=True)

    return response


# Signout Route
@router.post("/signout")
async def signout(user_id: str = Depends(verify_token)):
    if not user_id:
        raise HTTPException(status_code=400, detail="Authorization token missing")

    # Here you can add logic to invalidate the token if needed.
    # For example, if you're using JWT, you might want to blacklist this token
    # in the token storage (if any), or simply let it expire naturally.

    # Create a response and clear any cookie-based session if you're using them
    response = JSONResponse({"success": True, "message": "User logged out successfully"})
    response.delete_cookie("access_token")  # Clear the token from the cookies if applicable

    return response
