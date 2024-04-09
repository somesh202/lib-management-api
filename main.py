from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import certifi
ca = certifi.where()

app = FastAPI()

load_dotenv()

mongo_uri = os.getenv("DB_URI")
client = MongoClient(mongo_uri, tlsCAFile=ca)
db = client["cosmocloud"]
students_collection = db["lib"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Pydantic models
    
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address


@app.post("/students/", response_model=dict)
async def create_stud(student: Student):
    # insert student into db
    result = students_collection.insert_one(student.dict())
    inserted_id = result.inserted_id
    return {"id": str(inserted_id)}

@app.get("/students/", response_model=dict)
async def list_stud(country: str = Query(None), age: int = Query(None)):
    
    filter_query = {}
    if country:
        filter_query["address.country"] = country
    if age:
        filter_query["age"] = {"$gte": age}

    # Find students based on params filter
    students = list(students_collection.find(filter_query))
    return {"data": students}

@app.get("/students/{id}", response_model=Student)
async def read_stud(id: str):
    # Fetch student from db
    student = students_collection.find_one({"_id": ObjectId(id)})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}")
async def update_stud(id: str, student: Student):
    # Update student in db
    result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        return {"message": "Student updated successfully"}

@app.delete("/students/{id}")
async def delete_stud(id: str):
    # delete student from db
    result = students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        return {"message": "Student deleted successfully"}