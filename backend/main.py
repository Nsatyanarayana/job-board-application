from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.auth import router as auth_router
from routes.employer import router as employer_router
from routes.job_seeker import router as job_seeker_router
from routes.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "../frontend"), name="static")
templates = Jinja2Templates(directory="../frontend")


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(employer_router, prefix="/employer", tags=["Employer"])
app.include_router(job_seeker_router, prefix="/job_seeker", tags=["Job Seeker"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

        
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/employer/dashboard")
async def employer_dashboard(request: Request):
    return templates.TemplateResponse("employer/dashboard.html", {"request": request})

@app.get("/employer/post-job")
async def post_job(request: Request):
    return templates.TemplateResponse("employer/post-job.html", {"request": request})

@app.get("/job-seeker/dashboard")
async def job_seeker_dashboard(request: Request):
    return templates.TemplateResponse("job-seeker/dashboard.html", {"request": request})

@app.get("/job-seeker/profile")
async def job_seeker_profile(request: Request):
    return templates.TemplateResponse("job-seeker/profile.html", {"request": request})

@app.get("/job-seeker/report")
async def job_seeker_report(request: Request):
    return templates.TemplateResponse("job-seeker/report.html", {"request": request})

@app.get("/job-seeker/navbar")
async def job_seeker_navbar(request: Request):
    return templates.TemplateResponse("job-seeker/navbar.html", {"request": request})
@app.get("/admin")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin/admin.html", {"request": request})

