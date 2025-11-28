from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine, Base
from api.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Traffic Management Auth API")

# Allow all origins (for development/testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "online", "message": "Auth System Ready"}
