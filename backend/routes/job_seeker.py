import os
import shutil
from fastapi import APIRouter, File, Query, UploadFile, Form, HTTPException, Response
from typing import List, Optional
from fastapi.responses import JSONResponse, FileResponse
from bson import ObjectId, Binary
from utils.db import db
from models.schemas import Profile, Job, IssueReport
import google.generativeai as genai
import json
import PyPDF2
from io import BytesIO
import docx
import re
from uuid import uuid4
from datetime import datetime

RESUME_DIR = "resumes"
os.makedirs(RESUME_DIR, exist_ok=True)



GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

router = APIRouter()

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(BytesIO(file_content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from a file based on its MIME type."""
    file_content = file.file.read()
    if file.content_type == "application/pdf":
        return extract_text_from_pdf(file_content)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_content)
    elif file.content_type == "text/plain":
        return file_content.decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or plain text file.")
@router.get("/get_profile")
async def get_profile(user_id: str):
    user = db.users.find_one({"user_id": user_id}, {"resume_content": 0})
    if user:
        user["_id"] = str(user["_id"])
        return user
    else:
        return JSONResponse(content={"status": "error", "message": "User not found"}, status_code=404)
@router.post("/update-profile")
async def update_profile(
    user_id: str = Form(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    experience: Optional[str] = Form(None),
    job_preferences: Optional[str] = Form(None),
    education: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
):
    try:
        profile_data = {
            "user_id": user_id,
            "name": name,
            "phone": phone,
            "location": location,
            "skills": skills,
            "experience": experience,
            "job_preferences": job_preferences,
            "education": education,
            "social_links": social_links,
        }

        if resume:
            resume_text = extract_text_from_file(resume)
            prompt = f"""
            Extract the following details from the resume text below and format the response as key-value pairs do not use ""and, symbols:

            Full Name: <name>
            Phone Number: <phone>
            Location: <location>
            Skills: <skills>
            Experience: <experience>
            Job Preferences: <job_preferences>
            Education: <education>
            Social Links: <social_links>

            Resume Text:
            {resume_text}
            """
            response = model.generate_content(prompt)
            extracted_data = response.text.strip().split("\n")

            for line in extracted_data:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if "name" in key:
                        profile_data["name"] = value
                    elif "phone" in key:
                        profile_data["phone"] = value
                    elif "location" in key:
                        profile_data["location"] = value
                    elif "skills" in key:
                        profile_data["skills"] = value if value != "** Not specified in the text" else None
                    elif "experience" in key:
                        profile_data["experience"] = value if value != "** Not specified in the text" else None
                    elif "job preferences" in key:
                        profile_data["job_preferences"] = value if value != "** Not specified in the text" else None
                    elif "education" in key:
                        profile_data["education"] = value if value != "** Not specified in the text" else None
                    elif "social links" in key:
                        profile_data["social_links"] = value if value != "** Not specified in the text" else None

            
            resume_filename = f"{user_id}_{resume.filename}"
            resume_path = os.path.join(RESUME_DIR, resume_filename)
            resume.file.seek(0)
            with open(resume_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            profile_data["resume_filename"] = resume_filename
            profile_data["resume_path"] = resume_path

        existing_profile = db.users.find_one({"user_id": user_id})
        if existing_profile:
            db.users.update_one({"user_id": user_id}, {"$set": profile_data})
            return {"status": "success", "message": "Profile updated successfully"}
        else:
            db.users.insert_one(profile_data)
            return {"status": "success", "message": "Profile created successfully"}

    except ValueError as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Failed to process resume: {str(e)}"}, status_code=500)



@router.get("/resumes")
async def view_resumes(user_id: str):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    resumes = list(db.users.find({"user_id": user_id}, {"resume_filename": 1, "resume_path": 1, "_id": 0}))
    filename = resumes[0]["resume_filename"]
    RESUME_PATH = os.path.join(os.getcwd(), "resumes")
    file_path = os.path.join(RESUME_PATH, filename)
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for this user")
    print({"resumes": resumes})  
    return FileResponse(file_path)


@router.post("/apply")
async def apply_for_job(
    job_id: str = Form(...),
    user_id: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    resume: UploadFile = File(...),
):
    job = db.jobs.find_one({"job_id": job_id})
    if not job:
        return JSONResponse(content={"status": "error", "message": "Job not found"}, status_code=404)

    user = db.users.find_one({"user_id": user_id})
    if not user:
        return JSONResponse(content={"status": "error", "message": "User not found"}, status_code=404)

    existing_application = db.applications.find_one({"job_id": job_id, "user_id": user_id})
    if existing_application:
        return JSONResponse(content={"status": "error", "message": "You have already applied for this job"}, status_code=400)

    resume_content = await resume.read()

    application_data = {
        "job_id": job_id,
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "resume_filename": resume.filename,
        "resume_content": resume_content,
        "status": "pending",
    }

    db.applications.insert_one(application_data)
    db.jobs.update_one({"job_id": job_id}, {"$push": {"applicants": user_id}})

    return JSONResponse(content={"status": "success", "message": "Successfully applied for the job!"})

@router.delete("/remove_application")
async def remove_application(job_id: str, user_id: str):
    application = db.applications.find_one({"job_id": job_id, "user_id": user_id})
    if not application:
        return JSONResponse(content={"status": "error", "message": "Application not found"}, status_code=404)

    db.applications.delete_one({"job_id": job_id, "user_id": user_id})
    db.jobs.update_one({"job_id": job_id}, {"$pull": {"applicants": user_id}})

    return {"status": "success", "message": f"Application for job {job_id} removed successfully"}

@router.get("/applications")
async def get_applications(user_id: str):
    applications = list(db.applications.find({"user_id": user_id}))
    application_list = []
    for application in applications:
        job_id = application["job_id"]
        job = db.jobs.find_one({"job_id": job_id}, {"_id": 0})
        if job:
            application_list.append({
                **job,
                "status": application.get("status", "applied"), 
            })

    if not application_list:
        return JSONResponse(content={"status": "error", "message": "No applications found"}, status_code=404)

    return {"status": "success", "applied_list": application_list}


@router.get("/jobs", response_model=Job)
async def get_jobs(userID: str):
    skills_string = db.users.find_one({"user_id": userID}, {"_id": 0, "skills": 1})
    skills = skills_string["skills"].split(',')
    skills = [skill.strip().lower() for skill in skills]

    jobs = list(db.jobs.find({"skills": {"$elemMatch": {"$regex": "|".join(skills), "$options": "i"}}}, {"_id": 0}))

    return JSONResponse(content=jobs)







@router.post("/report_issue/{user_id}")
async def report_issue(user_id: str, issue: IssueReport):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        return {"status": "error", "message": "User not found"}

    username = user.get("username")
    prompt = f"""
    A job seeker has reported the following issue:
    Issue Type: {issue.issue_type}
    Description: {issue.description}

    Please provide a detailed solution in only 50 words to solve this issue.
    """
    try:
        response = model.generate_content(prompt)
        solution = response.text.strip()
    except Exception as e:
        solution = "Unable to generate a solution at this time. Please contact support."

    unique_id = str(uuid4())

    issue_data = {
        "issue_id": unique_id,  
        "user_id": user_id,
        "username": username,
        "issue_type": issue.issue_type,
        "description": issue.description,
        "solution": solution,  
        "status": "open",
        "created_at": datetime.now(), 
    }
    db.issues.insert_one(issue_data)

    return {"status": "success", "message": "Issue reported successfully", "solution": solution, "issue_id": unique_id}
@router.get("/reported_issues")
async def get_reported_issues(user_id: str):
    issues = list(db.issues.find({"user_id": user_id}, {"_id": 0}))
    return {"issues": issues}


@router.delete("/remove_issue/{issue_id}")
async def remove_issue_by_id(issue_id: str):
    """
    Remove a specific issue by its custom ID.
    """

    result = db.issues.delete_one({"issue_id": issue_id})

    if result.deleted_count > 0:
        return {"status": "success", "message": f"Removed issue with ID {issue_id}"}
    else:
        return JSONResponse(
            content={"status": "error", "message": "Issue not found"},
            status_code=404,
        )
