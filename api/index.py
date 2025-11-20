from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import motor.motor_asyncio
import uuid
import os

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
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://clgworks2024_db_user:Rx5U0XJKuAWe0JRJ@cluster0.zyj1byl.mongodb.net/?appName=Cluster0"
)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client["verceldemo_db"]
collection = db["todos"]

# -----------------------
#    API ROUTES
# -----------------------

@app.get("/api/todos/", response_model=List[dict])
async def list_todos():
    docs = []
    cursor = collection.find({}).sort("_id", -1)
    async for d in cursor:
        docs.append(doc_to_todo(d))
    return docs


@app.post("/api/todos/", status_code=201)
async def create_todo(todo: TodoIn):
    new_id = uuid.uuid4().hex
    payload = {"_id": new_id, **todo.dict()}
    await collection.insert_one(payload)
    return {"id": new_id, **todo.dict()}


@app.put("/api/todos/{id}")
async def update_todo(id: str, todo: TodoIn):
    result = await collection.update_one({"_id": id}, {"$set": todo.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": id, **todo.dict()}


@app.delete("/api/todos/{id}")
async def delete_todo(id: str):
    result = await collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}


# Required for Vercel serverless
handler = app
