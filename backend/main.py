"""
FastAPI Backend - Gemini AI Integration
Managed with uv
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

from ai_assistant import stream_gemini_response, chat_with_history, generate_with_thinking
from constants import (
    DEFAULT_GEMINI_MODEL,
    GEMINI_3_PRO,
    TEMPERATURE
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Gemini AI Backend",
    description="FastAPI backend with latest Gemini models (3 Pro, 2.5 Pro, 2.5 Flash)",
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
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request model"""
    prompt: str
    model: Optional[str] = DEFAULT_GEMINI_MODEL
    temperature: Optional[float] = TEMPERATURE
    max_tokens: Optional[int] = None


class ChatHistoryRequest(BaseModel):
    """Chat with history request model"""
    messages: List[dict]  # [{"role": "user/assistant", "content": "..."}]
    model: Optional[str] = DEFAULT_GEMINI_MODEL
    temperature: Optional[float] = TEMPERATURE


class ThinkingRequest(BaseModel):
    """Thinking request model for complex reasoning"""
    prompt: str
    model: Optional[str] = GEMINI_3_PRO


class ModelsResponse(BaseModel):
    """Available models response"""
    models: dict


# ============================================================================
# GEMINI AI ENDPOINTS
# ============================================================================

@app.get("/api/models", response_model=ModelsResponse)
async def get_available_models():
    """Get list of available Gemini models"""
    return {
        "models": {
            "gemini-3-pro-preview": {
                "name": "Gemini 3 Pro",
                "description": "Best model for multimodal understanding",
                "context_window": "1M tokens",
                "use_case": "Complex multimodal tasks with text, images, video, audio"
            },
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "description": "State-of-the-art thinking model",
                "context_window": "1M tokens",
                "use_case": "Complex reasoning in code, math, and STEM domains"
            },
            "gemini-2.5-flash": {
                "name": "Gemini 2.5 Flash",
                "description": "Well-rounded with strong price-performance",
                "context_window": "1M tokens",
                "use_case": "Large-scale processing, low-latency, high volume tasks"
            },
            "gemini-2.5-flash-lite": {
                "name": "Gemini 2.5 Flash Lite",
                "description": "Fastest flash model optimized for cost-efficiency",
                "context_window": "1M tokens",
                "use_case": "Speed-prioritized applications with high throughput"
            }
        }
    }


@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    Stream chat response from Gemini

    Streams text chunks as they arrive from the model
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    async def generate():
        async for chunk in stream_gemini_response(
            prompt=request.prompt,
            model_name=request.model,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/chat/history")
async def chat_with_conversation_history(request: ChatHistoryRequest):
    """
    Stream chat response with conversation history

    Maintains context from previous messages
    """
    if not request.messages or len(request.messages) == 0:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    async def generate():
        async for chunk in chat_with_history(
            messages=request.messages,
            model_name=request.model,
            temperature=request.temperature
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/chat/thinking")
async def chat_with_thinking(request: ThinkingRequest):
    """
    Generate response with thinking process

    Uses Gemini 3 Pro or 2.5 Pro for complex reasoning
    Returns both thinking process and final response
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    result = await generate_with_thinking(
        prompt=request.prompt,
        model_name=request.model
    )

    return result


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
