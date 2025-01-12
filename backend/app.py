import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from pymongo import MongoClient
import uvicorn

# Load environment variables

load_dotenv()
# MONGO_URI = "mongodb://localhost:27017/notes"
# MongoDB Connection
mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
# client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client.get_database("notes")  # Replace with your database name

# FastAPI app initialization
app = FastAPI()
origins = [
    "*",  # Allow the frontend's origin,  # If needed, add more origins
]
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for parsing cookies (if you need them)
@app.middleware("http")
async def add_cookie(request: Request, call_next):
    cookies = request.cookies  # Access cookies here
    response = await call_next(request)
    return response

# Import routers
from controller import auth_controller , note_controller
# from routes import auth_route , note_route
# from ro import router as note_router

# Include routers in the app
app.include_router(auth_controller.router)
# app.include_router(auth_router, prefix="/api/auth")
app.include_router(note_controller.router)
# app.include_router(note_route.router)
# app.include_router(note_router, prefix="/api/auth")


# Error handling
@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    status_code = 500
    message = "Internal Server Error"
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "statusCode": status_code, "message": message},
    )

# Define the lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await startup_db()
    
    # Yield control back to FastAPI
    yield
    
    # Shutdown logic
    await shutdown_db()

# Define the startup function
async def startup_db():
    try:
        client.server_info()  # This will trigger an exception if the connection fails
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="MongoDB connection failed")

# Define the shutdown function
async def shutdown_db():
    client.close()  # Close the MongoDB client when the app shuts down

# Attach the lifespan function to FastAPI
# app = FastAPI(title="notes",
#               description="Backend",
#               version="0.1.0",
#               redoc_url='/redoc')


HOST = "127.0.0.1"  # Localhost
PORT = 8000  # Port you want to run the app on
LOG_LEVEL = "info"  # Set log level (e.g., "debug", "info", "warning")

if __name__ == '__main__':
    uvicorn.run("app:app", host=HOST, port=PORT, log_level=LOG_LEVEL, reload=True)

