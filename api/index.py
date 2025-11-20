from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
import os
import motor.motor_asyncio
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins (or restrict to your frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoIn(BaseModel):
    title: str
    done: bool = False

def doc_to_todo(doc: dict) -> dict:
    return {"id": str(doc.get("_id")), "title": doc.get("title", ""), "done": bool(doc.get("done", False))}

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://clgworks2024_db_user:Rx5U0XJKuAWe0JRJ@cluster0.zyj1byl.mongodb.net/?appName=Cluster0",
)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client["verceldemo_db"]
collection = db["todos"]

router = APIRouter(prefix="/api/todos")

@router.get("/", response_model=List[dict])
async def list_todos():
    docs = []
    cursor = collection.find({}).sort("_id", -1)
    async for d in cursor:
        docs.append(doc_to_todo(d))
    return docs

@router.post("/", status_code=201)
async def create_todo(todo: TodoIn):
    new_id = uuid.uuid4().hex
    payload = {"_id": new_id, **todo.dict()}
    await collection.insert_one(payload)
    return {"id": new_id, **todo.dict()}

@router.put("/{id}")
async def update_todo(id: str, todo: TodoIn):
    result = await collection.update_one({"_id": id}, {"$set": todo.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": id, **todo.dict()}

@router.delete("/{id}")
async def delete_todo(id: str):
    result = await collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}

app.include_router(router)
