from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    createdAt: datetime = datetime.now()

class UserResponse(UserBase):
    id: str

    class Config:
        orm_mode = True
