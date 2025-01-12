from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    isPinned: Optional[bool] = False
    summary: str

class NoteCreate(NoteBase):
    pass

class NoteInDB(NoteBase):
    userId: str
    createdAt: datetime = datetime.now()

class NoteResponse(NoteInDB):
    id: str

    class Config:
        orm_mode = True
