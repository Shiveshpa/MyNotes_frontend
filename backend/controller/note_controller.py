from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
# from transformers import pipeline
from bson import ObjectId
from utils.verifyUser import verify_token
from fastapi import Query, HTTPException, Depends
from bson import ObjectId
import requests
import openai
from dotenv import load_dotenv
from pymongo import MongoClient
import os 

# MongoDB connection
# client = AsyncIOMotorClient("mongodb://localhost:27017")

# load_dotenv()

load_dotenv()

# Retrieve the MongoDB URI from environment variables
mongodb_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB using the URI
client = AsyncIOMotorClient(mongodb_uri)
db = client.smart_notes
from fastapi import APIRouter
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
# tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
# model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

router = APIRouter()

# Pydantic models for request/response
class NoteModel(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    isPinned: Optional[bool] = False

class UpdateNoteModel(BaseModel):
    title: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]
    isPinned: Optional[bool]

# Utility to check note ownership
def fix_object_ids(note):
    """Convert ObjectId to str in a MongoDB document."""
    if isinstance(note, dict):
        for key, value in note.items():
            if isinstance(value, ObjectId):
                note[key] = str(value)
    return note
async def check_note_ownership(note_id: str, user_id: str):
    note = await db.notes.find_one({"_id": ObjectId(note_id), "userId": user_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or permission denied")
    return note

def summarize_with_transformers(content: str) -> str:
    # Generate the summary using the model
    # summary_result = summarizer(content, max_length=150, min_length=50, do_sample=False)
    # return summary_result[0]['summary_text']

    completion = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the model (e.g., gpt-4)
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text in short containing all the content but the summary should be in short if not sensible text then write the content does not seem sensible no need to return long responses as anyways we are just required the summary:\n{content}"}
        ]
    )
    
    summary = completion.choices[0].message['content']
    return summary
# Add a new note
@router.post("/add")
async def add_note(note: NoteModel, token: str = Depends(verify_token)):
    # Verify the token and get user_id from it
    user_id = token  # Assuming verify_token returns user info with user_id

    # Ensure title and content are not empty
    if not note.title or not note.content:
        raise HTTPException(status_code=400, detail="Title and Content are required")

    summary = None
    if len(note.content) > 50:  # You can set a minimum content length for summarization
        try:
            # Call the Hugging Face API for summarization
            summary = summarize_with_transformers(note.content)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
    else:
        summary = "Content too short for summarization."    

    # Prepare the note data for insertion
    new_note = {
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "userId": user_id,  # Associate the note with the user
        "isPinned": note.isPinned,
        "summary": summary
    }

    # Insert the note into the database
    result = await db.notes.insert_one(new_note)
    created_note = await db.notes.find_one({"_id": result.inserted_id})

    # Convert ObjectId to string for the response
    if created_note:
        created_note["_id"] = str(created_note["_id"])
        created_note["userId"] = str(created_note["userId"])

    return {"success": True, "message": "Note added successfully", "note": created_note}
# Edit a note
@router.put("/edit")
async def edit_note(updated_note: NoteModel, note_id: str = Query(...), user_id: str = Depends(verify_token)):
    # Check ownership
    print(f"Editing note with ID: {note_id}")
    print(f"Requested by user ID: {user_id}")

    # Ensure the note belongs to the user
    note = await check_note_ownership(note_id, user_id)

    # Filter out None values from updated note data
    update_data = {k: v for k, v in updated_note.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No changes provided")
    
    if "content" in update_data and update_data["content"]:
        content = update_data["content"]
        
        if len(content) > 50:  # Ensure content is long enough for summarization
            # Use the transformers summarize function
            summary_text = summarize_with_transformers(content)
            update_data["summary"] = summary_text
        else:
            update_data["summary"] = "Content too short for summarization."


    # Update the note in the database
    await db.notes.update_one({"_id": ObjectId(note_id)}, {"$set": update_data})

    # Fetch the updated note
    updated_note = await db.notes.find_one({"_id": ObjectId(note_id)})

    # Convert ObjectId to string for JSON serialization
    if updated_note:
        updated_note["_id"] = str(updated_note["_id"])
        updated_note["userId"] = str(updated_note["userId"])

    return {"success": True, "message": "Note updated successfully", "note": updated_note}


@router.get("/all")
async def get_all_notes(user_id: str = Depends(verify_token)):
    print(type(user_id))
    print("the user id is ",user_id)
    # print(user_id['id'])
    # notes = await db.notes.find({"userId": user_id}).sort("isPinned", -1).to_list(100)
    notes_cursor = db.notes.find({"userId": user_id}).sort("isPinned", -1)
    notes = await notes_cursor.to_list(length=100)
    print(notes)
    notes = [fix_object_ids(note) for note in notes]
    return {"success": True, "message": "All notes retrieved successfully", "notes": notes}
# Delete a note
@router.delete("/delete")
async def delete_note(note_id: str = Query(...), user_id: str = Depends(verify_token)):
    # Check if the user owns the note
    note = await check_note_ownership(note_id, user_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not authorized to delete")

    await db.notes.delete_one({"_id": ObjectId(note_id)})

    return {"success": True, "message": "Note deleted successfully"}

# Update the pinned status of a note
@router.put("/notes/{note_id}/pinned")
async def update_note_pinned(note_id: str, isPinned: bool, user_id: str):
    note = await check_note_ownership(note_id, user_id)

    await db.notes.update_one({"_id": ObjectId(note_id)}, {"$set": {"isPinned": isPinned}})
    updated_note = await db.notes.find_one({"_id": ObjectId(note_id)})

    return {"success": True, "message": "Note updated successfully", "note": updated_note}

# Search notes by title or content
def note_serializer(note) -> dict:
    """Helper function to convert MongoDB note document to a serializable format"""
    return {
        "_id": str(note["_id"]),  # Convert ObjectId to string
        "title": note["title"],
        "content": note["content"],
        "tags": note.get("tags", []),
        "userId": note["userId"],
        "isPinned": note.get("isPinned", False)
    }

@router.get("/notes/search")
async def search_note(query: str = Query(...), user_id: str = Depends(verify_token)):
    # Ensure query is provided
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")

    # Find notes that match the query in title, content, or tags for the user
    matching_notes = await db.notes.find({
        "userId": user_id,  # Ensure the note belongs to the authenticated user
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},   # Search in title
            {"content": {"$regex": query, "$options": "i"}},  # Search in content
            {"tags": {"$regex": query, "$options": "i"}}      # Search in tags
        ]
    }).to_list(100)

    # Convert each note to a serializable format
    serialized_notes = [note_serializer(note) for note in matching_notes]

    return {
        "success": True,
        "message": "Notes matching the search query retrieved successfully",
        "notes": serialized_notes
    }