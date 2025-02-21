from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile, Form,File

class User(BaseModel):
    username: str
    email: str
    password: str
    role: str  
    profile: Optional[dict] = {}

class Job(BaseModel):
    title: str
    description: str
    skills: List[str]
    salary: str
    location: str

class Profile(BaseModel):
    user_id: str = Form(...)
    name: str = Form(...)
    phone: str = Form(...)
    location: str = Form(...)
    skills: str = Form(...)  
    experience: dict = Form(...) 
    job_preferences: str = Form(...)
    education: str = Form(...)
    resume: UploadFile = File(...)
    social_links: Optional[dict] = Form(...)

class EmployerProfile(BaseModel):
    user_id: str
    company_name: str
    position: str
    location: str

class EditJob(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    salary: Optional[float] = None
    location: Optional[str] = None

class IssueReport(BaseModel):
    issue_type: str
    description: str

class generate_content(BaseModel):
    prompt: str
    response: Optional[str] = None
    user_id: Optional[str] = None