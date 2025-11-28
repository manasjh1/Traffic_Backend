from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine, Base
from api.auth import router as auth_router

# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Traffic Management Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://traffic-project-frontend.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "online", "message": "Auth System Ready"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "healthy"}
