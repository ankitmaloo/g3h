"""
FastAPI Backend - Main Application
Managed with uv
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Backend",
    description="Backend API built with FastAPI and uv",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# BASE ENDPOINTS
# ============================================================================

@app.get("/")
async def hello_world():
    """Hello World endpoint"""
    return {"message": "Hello World!"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

# Add your custom endpoints below
# Example:
# @app.post("/api/chat")
# async def chat_endpoint(request: ChatRequest):
#     """Chat endpoint"""
#     # Implementation here
#     pass
