from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from utils.db import db
from bson import ObjectId
import google.generativeai as genai
import os

# Set Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

def generate_issue_response_prompt(issue_description):
    prompt = f"""
    You are a support assistant. Respond to the following user issue:
    {issue_description}

    Provide a professional and helpful response that:
    1. Acknowledges the issue.
    2. Offers a solution or next steps.
    3. Assures the user that their concern is being addressed.
    """
    return prompt

@router.get("/stats")
async def get_statistics():
    total_users = db.users.count_documents({"role": {"$in": ["job_seeker", "employer"]}})
    total_jobs = db.jobs.count_documents({})
    applications = db.applications.find({}, {"job_id": 1, "_id": 0})

    job_application_count = {}
    for application in applications:
        job_id = application["job_id"]
        job_application_count[job_id] = job_application_count.get(job_id, 0) + 1

    most_applied_jobs = []
    for job_id, application_count in job_application_count.items():
        job = db.jobs.find_one({"job_id": job_id}, {"_id": 0})
        if job:
            job["application_count"] = application_count
            most_applied_jobs.append(job)

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "most_applied_jobs": most_applied_jobs
    }

@router.get("/users/employers")
async def get_users():
    users = list(db.users.find({"role": {"$in": ["job_seeker", "employer"]}}, {"_id": 0, "resume_content": 0}))
    return JSONResponse(content=users)

@router.get("/job_postings")
async def get_job_postings():
    jobs = list(db.jobs.find({}, {"_id": 0}))
    return JSONResponse(content=jobs)

@router.get("/issues")
async def get_reported_issues():
    issues = list(db.issues.find({}, {"_id": 0}))
    if not issues:
        return JSONResponse(content={"message": "No issues reported yet"}, status_code=404)
    return {"reported_issues": issues}

@router.post("/respond_to_issue")
async def respond_to_issue(issue_id: str, response_text: str):
    issue = db.issues.find_one({"issue_id": issue_id})
    if not issue:
        return JSONResponse(content={"message": "Issue not found"}, status_code=404)

    # Generate a response using Gemini
    prompt = generate_issue_response_prompt(issue["description"])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    generated_response = response.text

    # Save the response to the database
    db.issues.update_one(
        {"issue_id": issue_id},
        {"$set": {"admin_response": generated_response, "status": "resolved"}}
    )
    return {"status": "success", "message": "Issue resolved", "response": generated_response}