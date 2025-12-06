"""
Image Generator Module
Generate images from reference images using Gemini's image generation API.

Uses gemini-3-pro-image-preview model with 4K resolution.
"""

import base64
import os
from typing import Optional

from google import genai
from google.genai import types

# Generic prompt (no secret info yet - to be enhanced later)
DEFAULT_IMAGE_PROMPT = """Generate a professional high-quality digital portrait 
incorporating the visual elements and style from the provided reference images. 
Create a cohesive, polished result that blends the references harmoniously."""

# Check if we're in mock mode (no API key)
MOCK_MODE = not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY")


async def generate_image_from_references(
    reference_images: list[bytes],
    prompt: str = DEFAULT_IMAGE_PROMPT,
    model: str = "gemini-3-pro-image-preview",
) -> bytes:
    """
    Generate an image from reference images using Gemini.
    
    Args:
        reference_images: List of image bytes (up to 5 reference images)
        prompt: Text prompt describing what to generate
        model: Gemini model to use (default: gemini-3-pro-image-preview)
    
    Returns:
        Generated image as bytes
    
    Raises:
        ValueError: If no image in response or API error
    """
    # Mock mode: return the first reference image as-is for smoke testing
    if MOCK_MODE:
        print("[MOCK MODE] No API key found, returning first reference image")
        if reference_images:
            return reference_images[0]
        raise ValueError("No reference images provided in mock mode")
    
    # Create client (uses GOOGLE_API_KEY or GEMINI_API_KEY env var)
    client = genai.Client()
    
    # Build contents with prompt and reference images
    contents = [prompt]
    for img_bytes in reference_images:
        # Detect mime type from image bytes
        mime_type = _detect_mime_type(img_bytes)
        contents.append(
            types.Part.from_bytes(
                data=img_bytes,
                mime_type=mime_type
            )
        )
    
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    image_size="4K",
                ),
            ),
        )
        
        # Extract image from response
        for part in response.parts:
            if part.inline_data:
                return base64.b64decode(part.inline_data.data)
        
        raise ValueError("No image in response from Gemini API")
        
    except Exception as e:
        raise ValueError(f"Image generation failed: {str(e)}")
    finally:
        await client.aio.aclose()


def _detect_mime_type(image_bytes: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    elif image_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    else:
        return "image/png"  # Default fallback
