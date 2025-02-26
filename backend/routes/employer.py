import os,requests
import google.generativeai as genai
from fastapi import APIRouter, Form, HTTPException
from models.schemas import Job, EmployerProfile
from utils.db import db

from fastapi.responses import JSONResponse
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

router = APIRouter()

@router.put("/update_profile")
async def update_profile(profile: EmployerProfile):
    user = db.users.find_one({"user_id": profile.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile_data = profile.dict()
    db.users.update_many(
        {"user_id": profile.user_id},
        {"$set": profile_data}
    )
    return {"message": "Employer profile updated successfully"}

@router.get("/all_jobs")
async def get_all_jobs():
    jobs = list(db.jobs.find({}, {"_id": 0}))
    return JSONResponse(content=jobs)

@router.get("/get_profile/{user_id}")
async def get_profile(user_id: str):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = {key: user[key] for key in user if key != "_id"}
    return JSONResponse(content=user_profile)

@router.post("/post_job")
async def post_job(job: Job, user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    try:
        prompt = (
            f"Title: {job.title}\n\n"
            f"Location: {job.location}\n\n"
            f"Skills: {', '.join(job.skills)}\n\n"
            "Paragraph:\n"
            "Create a professional job description for the above position. "
            "The description should be approximately 150 words long and include the following details:\n\n"
            "- Key responsibilities of the role\n"
            "- Required qualifications and skills\n"
            "- Location and any location-specific requirements\n"
            "- Any additional relevant details\n\n"
            "Ensure that the text is structured in paragraph format, free from markdown symbols, and written in a formal yet engaging tone."
              "Ensure that the text is structured in paragraph format, uses bullet points (•) instead of markdown symbols, and is written in a formal yet engaging tone."
        )
        response = model.generate_content(prompt)
        generated_description = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate job description: {str(e)}")


    job_data = job.dict()
    unique_id = str(uuid.uuid1())

    data = {
        "title": job_data["title"],
        "description": generated_description,  
        "skills": job_data["skills"],
        "salary": job_data["salary"],
        "location": job_data["location"],
        "job_id": unique_id,
        "user_id": user_id
    }

    db.jobs.insert_one(data)
    return {"message": "Job posted successfully with generated description"}

@router.get("/generate_description")
async def generate_description(title: str, skills: str, location: str, user_id: str):
    if not title:
        raise HTTPException(status_code=400, detail="Job title is required")
    if not skills:
        raise HTTPException(status_code=400, detail="Skills are required")
    if not location:
        raise HTTPException(status_code=400, detail="Location is required")

    try:
        prompt = (
            f"Title: {title}\n\n"
            f"Location: {location}\n\n"
            f"Skills: {', '.join(skills)}\n\n"
            "Paragraph:\n"
            "Create a professional job description for the above position. "
            "The description should be approximately 150 words long and include the following details:\n\n"
            "- Key responsibilities of the role\n"
            "- Required qualifications and skills\n"
            "- Location and any location-specific requirements\n"
            "- Any additional relevant details\n\n"
            "Ensure that the text is structured in paragraph format, free from markdown symbols, and written in a formal yet engaging tone."
              "Ensure that the text is structured in paragraph format, uses bullet points (•) instead of markdown symbols, and is written in a formal yet engaging tone."
        )
        response = model.generate_content(prompt)
        generated_description = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate job description: {str(e)}")

    return {"description": generated_description}


@router.get("/jobs/{user_id}")
async def get_jobs(user_id: str):
    jobs = list(db.jobs.find({"user_id": user_id}, {"_id": 0}))  
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for this employer")
    return JSONResponse(content=jobs)

@router.put("/edit_job/{job_id}")
async def edit_job(job_id: str, updated_job: dict):
    result = db.jobs.update_one({"job_id": job_id}, {"$set": updated_job})
    if result.matched_count == 0:
        return {"message": "Job not found"}

    return {"message": "Job updated successfully"}

@router.post("/update_application_status")
async def update_application_status(
    job_id: str = Form(...),
    user_id: str = Form(...),
    status: str = Form(...),  
):
    application = db.applications.find_one({"job_id": job_id, "user_id": user_id})
    if not application:
        return JSONResponse(content={"status": "error", "message": "Application not found"}, status_code=404)

    db.applications.update_one(
        {"job_id": job_id, "user_id": user_id},
        {"$set": {"status": status}}
    )

    return {"status": "success", "message": f"Application status updated to {status}"}

@router.get("/view_application_details/{user_id}")
async def view_application_details(user_id: str):
    jobs = list(db.jobs.find({"user_id": user_id}, {"_id": 0}))
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for this employer")

    job_ids = [job["job_id"] for job in jobs]
    applications = list(db.applications.find({"job_id": {"$in": job_ids}}, {"_id": 0, "resume_content": 0}))
    if not applications:
        raise HTTPException(status_code=404, detail="No applications found for these jobs")

    users = {app["user_id"]: db.users.find_one({"user_id": app["user_id"]}, {"_id": 0, "resume_content": 0}) 
             for app in applications if app["user_id"]}

    return JSONResponse(content={
        "applications": applications,
        "jobs": jobs,
        "users": list(users.values())
    })

@router.delete("/delete_job/{job_id}")
async def delete_job(job_id: str):
    result = db.jobs.delete_one({"job_id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Job deleted successfully"}