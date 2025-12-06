"""
FastAPI Backend - Gemini AI Integration
Managed with uv
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import base64
import os

from ai_assistant import stream_gemini_response, chat_with_history, generate_with_thinking
from constants import (
    DEFAULT_GEMINI_MODEL,
    GEMINI_3_PRO,
    TEMPERATURE
)
from image_generator import generate_image_from_references, MOCK_MODE
from watermark import embed_watermark, decode_watermark

# Load environment variables
load_dotenv()
print("API KEY = ", os.getenv("GEMINI_API_KEY"))

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
# IMAGE GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/generate-image")
async def generate_image(
    files: list[UploadFile] = File(...),
    watermark_text: Optional[str] = Form(None)
):
    """
    Generate image from reference images with optional invisible watermark.
    
    Accepts up to 5 reference images (PNG, JPG, WEBP).
    If watermark_text is provided, embeds it invisibly using DCT.
    Returns generated image as base64 encoded string.
    
    In mock mode (no API key), returns the first reference image.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one image file is required")
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reference images allowed")
    
    # Read uploaded files
    reference_images = []
    for file in files:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"Empty file: {file.filename}")
        reference_images.append(content)
    
    try:
        # Generate image
        result_bytes = await generate_image_from_references(reference_images)
        
        # Embed watermark if text provided
        watermark_embedded = False
        if watermark_text and watermark_text.strip():
            print(f"[Watermark] Embedding {len(watermark_text)} bytes of hidden data")
            result_bytes = embed_watermark(result_bytes, watermark_text)
            watermark_embedded = True
        
        # Return as base64
        result_base64 = base64.b64encode(result_bytes).decode('utf-8')
        
        return JSONResponse(content={
            "image": result_base64,
            "mock_mode": MOCK_MODE,
            "watermark_embedded": watermark_embedded
        })
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


# ============================================================================
# VERIFY ENDPOINTS
# ============================================================================

@app.post("/api/verify")
async def verify_image(file: UploadFile = File(...)):
    """
    Extract hidden watermark from image using DCT frequency domain analysis.
    
    Accepts a single image file.
    Returns extracted hidden data if found.
    """
    if not file:
        raise HTTPException(status_code=400, detail="An image file is required")
    
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail=f"Empty file: {file.filename}")
    
    # Decode watermark from image
    extracted_data = decode_watermark(content)
    has_watermark = extracted_data is not None and len(extracted_data) > 0
    
    if has_watermark:
        analysis_result = f"""
=== WATERMARK DETECTED ===
File: {file.filename}
Size: {len(content)} bytes

Status: HIDDEN DATA EXTRACTED

The DCT frequency analysis detected an embedded
steganographic payload in the image high-frequency
components.

Extracted payload size: {len(extracted_data)} bytes
Signature: VERIFIED
===========================
"""
    else:
        analysis_result = f"""
=== ANALYSIS COMPLETE ===
File: {file.filename}
Size: {len(content)} bytes

Status: NO WATERMARK FOUND

The DCT frequency analysis did not detect
any embedded steganographic data in the
image high-frequency components.
=========================
"""
    
    return JSONResponse(content={
        "analysis": analysis_result.strip(),
        "verified": has_watermark,
        "extracted_data": extracted_data,
        "mock_mode": MOCK_MODE
    })


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # To start the server, run:
    # uv run python main.py
    import trio
    from hypercorn.config import Config
    from hypercorn.trio import serve
    
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    
    print(f"Starting server on http://0.0.0.0:8000")
    print(f"Mock mode: {MOCK_MODE}")
    
    trio.run(serve, app, config)
