from fastapi import FastAPI, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from config.db import connection
from fastapi.templating import Jinja2Templates
from bson import ObjectId

# Create a new APIRouter instance for the note routes
note = APIRouter()

# Initialize Jinja2Templates instance for rendering HTML templates
templates = Jinja2Templates(directory="templates")

# Route to retrieve all notes and render them in index.html
@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    docs = connection.notes.notes.find({})
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id": doc["_id"],
            "title": doc["title"],
            "desc": doc["desc"],
        })
    return templates.TemplateResponse(
        request=request, name="index.html", context={"newDocs": newDocs}
    )

# Route to create a new note
@note.post("/")
async def create_item(request: Request):
    form = await request.form()
    formDict = dict(form)
    note = connection.notes.notes.insert_one(formDict)
    return {"Success": True}

# Route to delete a note
@note.post("/delete/{note_id}")
async def delete_item(note_id: str):
    # Delete the note with the specified note_id
    result = connection.notes.notes.delete_one({"_id": ObjectId(note_id)})
    # Check if deletion was successful
    if result.deleted_count == 1:
        return {"Success": True}
    else:
        return {"Success": False, "error": "Note not found"}

# Route to retrieve a note for updating
@note.get("/update/{note_id}", response_class=HTMLResponse)
async def update_item(request: Request, note_id: str):
    doc = connection.notes.notes.find_one({"_id": ObjectId(note_id)})
    note_data = {
        "title": doc["title"],
        "desc": doc["desc"],
    }
    return templates.TemplateResponse(
        request=request, name="update.html", context={"note_id": note_id, "note_data": note_data}
    )

# Route to update a note
@note.post("/update/{note_id}")
async def update_item(request: Request, note_id: str, title: str = Form(...), desc: str = Form(...)):
    result = connection.notes.notes.update_one({"_id": ObjectId(note_id)}, {"$set": {"title": title, "desc": desc}})
    if result.modified_count == 1:
        return {"Success": True}
    else:
        return {"Success": False, "error": "Note not found or no changes were made"}
