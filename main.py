from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from api.content import router as content_router
import uvicorn

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="DailySync UPSC",
    description="DailySync UPSC is a platform for UPSC aspirants to prepare for the UPSC exam.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(content_router, prefix="/api", tags=["Content"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to DailySync UPSC",
        "frontend": "https://dailysync-upsc.netlify.app",
        "backend": "https://dailysync-upsc-416562352574.europe-west1.run.app",
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

