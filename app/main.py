from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.types import TypeDecorator
import json
from fastapi.middleware.cors import CORSMiddleware
#request to keep server alive
import threading
import requests

def keep_alive():
    try:
        # Replace 'your-app-url' with your Render app URL
        requests.get("https://phase-3-project-backend.onrender.com")
    except requests.exceptions.RequestException:
        pass  # Ignore any errors

    # Schedule the function to run again in 5 minutes
    threading.Timer(300, keep_alive).start()

# Start the keep-alive function when the app starts
keep_alive()
#keep alive ends here

# Initialize FastAPI app
app = FastAPI()

# Define allowed origins
# origins = [
#     # "http://localhost:5173",  # Frontend origin
#     # "http://127.0.0.1:5173",  # Alternative localhost
#     "https://phase-3-project-frontend-nine.vercel.app/" #remote host
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Database configuration
DATABASE_URL = "sqlite:///./careconnect.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Custom JSON Type
class JSONEncodedText(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)  # Serialize to JSON string
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)  # Deserialize back to Python list
        return value

# Define the SQLAlchemy Person model
class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    disability_type = Column(String, nullable=False)
    disability_severity = Column(String, nullable=False)
    contact_number = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_number = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    medical_conditions = Column(JSONEncodedText, nullable=True)

    # Relationship to resources
    resources = relationship("Resource", back_populates="person")

# Define the SQLAlchemy Resource model
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Foreign key to Person table
    person_id = Column(Integer, ForeignKey("persons.id"))

    # Define relationship to Person model
    person = relationship("Person", back_populates="resources")

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define Pydantic models
class PersonCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    disability_type: str
    disability_severity: str
    contact_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    address: Optional[str] = None
    medical_conditions: Optional[List[str]] = []

class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ResourceResponse(ResourceCreate):
    id: int
    person_id: int

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models to Pydantic models

class PersonResponse(PersonCreate):
    id: int
    resources: List[ResourceResponse] = []

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models to Pydantic models

# Routes

# Get all registered persons
@app.get("/persons", response_model=List[PersonResponse])
async def get_persons(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    return persons

# Add a new person
@app.post("/persons", response_model=PersonResponse)
async def add_person(person_data: PersonCreate, db: Session = Depends(get_db)):
    person = Person(**person_data.dict())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

# Get a person by ID
@app.get("/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

# Update a person by ID
@app.put("/persons/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person_data: PersonCreate, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    for key, value in person_data.dict().items():
        setattr(person, key, value)
    db.commit()
    db.refresh(person)
    return person

# Delete a person by ID
@app.delete("/persons/{person_id}")
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return {"message": "Person deleted successfully"}

# CRUD for Resources

# Get all resources for a person
@app.get("/persons/{person_id}/resources", response_model=List[ResourceResponse])
async def get_resources(person_id: int, db: Session = Depends(get_db)):
    resources = db.query(Resource).filter(Resource.person_id == person_id).all()
    return resources

# Add a resource to a person
@app.post("/persons/{person_id}/resources", response_model=ResourceResponse)
async def add_resource(person_id: int, resource_data: ResourceCreate, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    resource = Resource(person_id=person_id, **resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

# Update a resource
@app.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(resource_id: int, resource_data: ResourceCreate, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    for key, value in resource_data.dict().items():
        setattr(resource, key, value)
    
    db.commit()
    db.refresh(resource)
    return resource

# Delete a resource by ID
@app.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}
