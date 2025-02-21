from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.employer import router as employer_router
from routes.job_seeker import router as job_seeker_router
from routes.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
     allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(employer_router, prefix="/employer", tags=["Employer"])
app.include_router(job_seeker_router, prefix="/job_seeker", tags=["Job Seeker"])
app.include_router(admin_router,prefix="/admin",tags=["Admin"])
