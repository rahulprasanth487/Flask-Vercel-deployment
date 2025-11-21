from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import motor.motor_asyncio
import uuid
import os
import traceback

app = FastAPI()

# Allow all origins (or restrict to your frontend domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model
class TodoIn(BaseModel):
    title: str
    done: bool = False

# Convert Mongo document → JSON
def doc_to_todo(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title", ""),
        "done": bool(doc.get("done", False)),
    }

# MongoDB
# MONGODB_URI =  os.environ.get("MONGODB_URI")
# Lazy initialization - connect on first use
client = None
db = None
collection = None

async def get_collection():
    global client, db, collection
    if client is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_URI"))
        db = client["verceldemo_db"]
        collection = db["todos"]
    return collection

# -----------------------
#    API ROUTES
# -----------------------

@app.get("/")
async def root():
    return "Welcome to the Todo API"

@app.get("/api/todos/health")
async def health_check():
    """Lightweight health endpoint that does not touch MongoDB.
    Returns a static set of sample todos for quick UI checks.
    """
    sample = [
        {"id": "sample-1", "title": "Sample todo 1", "done": False},
        {"id": "sample-2", "title": "Sample todo 2", "done": True},
    ]
    return {"status": "ok", "todos": sample}


@app.get("/api/todos/", response_model=List[dict])
async def list_todos():
    try:
        collection = await get_collection()
        docs = []
        cursor = collection.find({}).sort("_id", -1)
        async for d in cursor:
            docs.append(doc_to_todo(d))
        return docs
    except Exception as e:
        # Print full traceback for function logs
        print("Database error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=503, detail=f"Database connection error: {str(e)}")


@app.post("/api/todos/", status_code=201)
async def create_todo(todo: TodoIn):
    try:
        collection = await get_collection()
        new_id = uuid.uuid4().hex
        payload = {"_id": new_id, **todo.dict()}
        await collection.insert_one(payload)
        return {"id": new_id, **todo.dict()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {str(e)}")


@app.put("/api/todos/{id}")
async def update_todo(id: str, todo: TodoIn):
    try:
        collection = await get_collection()
        result = await collection.update_one({"_id": id}, {"$set": todo.dict()})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"id": id, **todo.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {str(e)}")


@app.delete("/api/todos/{id}")
async def delete_todo(id: str):
    try:
        collection = await get_collection()
        result = await collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {str(e)}")


# Required for Vercel serverless
handler = app
