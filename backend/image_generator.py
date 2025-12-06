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
Create a cohesive, polished result that blends the references harmoniously.

Your generation should be of high quality and worthy of sharing on social media and elsewhere. The bar is super high, pay close attention to fidelity and closeness with reference images.
"""

# Check if we're in mock mode (no API key)
MOCK_MODE = False #not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY")


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
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
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
        # Use generate_content (non-streaming) for simplicity in API
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"], # Explicitly ask for both if needed
                image_config=types.ImageConfig(
                    image_size="1K",
                ),
            ),
        )
        
        generated_image_bytes = None
        
        # Iterate through parts to handle text and image
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                
                # Handle Text
                if part.text:
                    print(f"[Gemini Text]: {part.text}")
                
                # Handle Image
                if part.inline_data:
                    inline_data = part.inline_data
                    data = inline_data.data
                    mime_type = inline_data.mime_type
                    
                    print(f"[Gemini Image] Received image with mime_type: {mime_type}")
                    
                    # It's raw bytes as per documentation logic
                    generated_image_bytes = data
                    
                    # Save locally
                    save_dir = "generated_images"
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    
                    import time
                    import mimetypes
                    timestamp = int(time.time())
                    ext = mimetypes.guess_extension(mime_type) or ".png"
                    filename = f"{save_dir}/gen_{timestamp}{ext}"
                    
                    with open(filename, "wb") as f:
                        f.write(data)
                    print(f"Saved generated image to {filename}")

        if generated_image_bytes:
            return generated_image_bytes
            
        raise ValueError("No image found in Gemini API response")

    except Exception as e:
        # Check if it's a blocked response (safety)
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
             print(f"Safety Feedback: {e.response.prompt_feedback}")
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
