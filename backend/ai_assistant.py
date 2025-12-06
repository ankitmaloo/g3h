"""
Gemini AI Assistant Integration
Supports latest Gemini models: 3 Pro, 2.5 Pro, 2.5 Flash
"""

import google.generativeai as genai
from constants import settings
from typing import AsyncGenerator, Optional


# Configure Gemini API
genai.configure(api_key=settings.google_api_key)


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
        model = genai.GenerativeModel(model_name)

        generation_config = {
            "temperature": temperature,
        }

        if max_output_tokens:
            generation_config["max_output_tokens"] = max_output_tokens

        response = model.generate_content(
            prompt,
            stream=True,
            generation_config=generation_config
        )

        for chunk in response:
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
        model = genai.GenerativeModel(model_name)

        # Convert messages to Gemini format
        chat = model.start_chat(history=[])

        # Add history (all but last message)
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            chat.history.append({
                "role": role,
                "parts": [msg["content"]]
            })

        # Stream the latest message
        last_message = messages[-1]["content"]

        response = chat.send_message(
            last_message,
            stream=True,
            generation_config={"temperature": temperature}
        )

        for chunk in response:
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
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(prompt)

        # Extract thinking and final response if available
        thinking_parts = []
        response_parts = []

        for part in response.parts:
            if hasattr(part, 'thought') and part.thought:
                thinking_parts.append(str(part))
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
