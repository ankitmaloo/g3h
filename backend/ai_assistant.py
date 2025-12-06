"""
Gemini AI Assistant Integration
Supports latest Gemini models: 3 Pro, 2.5 Pro, 2.5 Flash

Updated to use new google-genai SDK
"""

import os
from google import genai
from google.genai import types
from constants import settings
from typing import AsyncGenerator, Optional


def _get_client() -> genai.Client:
    """Get a configured Gemini client"""
    api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


async def stream_gemini_response(
    prompt: str,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """
    Stream text response from Gemini

    Args:
        prompt: User's prompt/message
        model_name: Gemini model to use (gemini-3-pro-preview, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite)
        temperature: Controls randomness (0.0-2.0)
        max_output_tokens: Maximum tokens in response

    Yields:
        Text chunks as they arrive
    """
    try:
        client = _get_client()
        
        config_dict = {"temperature": temperature}
        if max_output_tokens:
            config_dict["max_output_tokens"] = max_output_tokens

        async for chunk in await client.aio.models.generate_content_stream(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**config_dict)
        ):
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"Error: {str(e)}"


async def chat_with_history(
    messages: list[dict],
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    Stream chat response with conversation history

    Args:
        messages: List of message dicts with 'role' and 'content'
        model_name: Gemini model to use
        temperature: Controls randomness (0.0-2.0)

    Yields:
        Text chunks as they arrive
    """
    try:
        client = _get_client()
        
        # Convert messages to Gemini content format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        async for chunk in await client.aio.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(temperature=temperature)
        ):
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"Error: {str(e)}"


async def generate_with_thinking(
    prompt: str,
    model_name: str = "gemini-3-pro-preview"
) -> dict:
    """
    Generate response with thinking process (non-streaming for thinking models)

    Args:
        prompt: User's prompt/message
        model_name: Thinking-capable model (gemini-3-pro-preview or gemini-2.5-pro)

    Returns:
        Dict with 'thinking' and 'response' fields
    """
    try:
        client = _get_client()

        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        # Extract thinking and final response if available
        thinking_parts = []
        response_parts = []

        for part in response.candidates[0].content.parts:
            if hasattr(part, 'thought') and part.thought:
                thinking_parts.append(str(part.text) if hasattr(part, 'text') else str(part))
            elif hasattr(part, 'text') and part.text:
                response_parts.append(part.text)

        return {
            "thinking": "\n".join(thinking_parts) if thinking_parts else None,
            "response": "\n".join(response_parts) if response_parts else response.text
        }

    except Exception as e:
        return {
            "thinking": None,
            "response": f"Error: {str(e)}"
        }

