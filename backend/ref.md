# Gemini AI Backend API Reference

FastAPI backend with the latest Gemini models (2025).

## Available Models

- **gemini-3-pro-preview**: Best model for multimodal understanding (1M token context)
- **gemini-2.5-pro**: State-of-the-art thinking model for complex reasoning
- **gemini-2.5-flash**: Well-rounded with strong price-performance (default)
- **gemini-2.5-flash-lite**: Fastest, optimized for cost-efficiency

## Setup

1. Copy environment file:
```bash
cp .env.example .env
```

2. Add your Google API key to `.env`:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

3. Install dependencies:
```bash
uv sync
```

4. Run the server:
```bash
uv run uvicorn main:app --reload --port 8000
```

## API Endpoints

### GET /

Hello World endpoint

**Example**:
```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "message": "Hello World!"
}
```

---

### GET /health

Health check endpoint

**Example**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy"
}
```

---

### GET /api/models

Get list of available Gemini models with their capabilities

**Example**:
```bash
curl http://localhost:8000/api/models
```

**Response**:
```json
{
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
```

**Expected behavior**: Returns metadata about all available Gemini models

---

### POST /api/chat/stream

Stream chat response from Gemini (uses default model: gemini-2.5-flash)

**Example**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms"
  }'
```

**With custom model and parameters**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "model": "gemini-2.5-pro",
    "temperature": 0.5,
    "max_tokens": 1000
  }'
```

**Request body**:
```json
{
  "prompt": "Your question or instruction here",
  "model": "gemini-2.5-flash",  // Optional, defaults to gemini-2.5-flash
  "temperature": 0.7,  // Optional, 0.0-2.0
  "max_tokens": null  // Optional, limits response length
}
```

**Response** (streaming):
```
Quantum computing is a type of computing that uses quantum bits...
```

**Expected behavior**: Streams text chunks in real-time as the model generates them

---

### POST /api/chat/history

Stream chat response with conversation history (maintains context)

**Example**:
```bash
curl -X POST http://localhost:8000/api/chat/history \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Python?"},
      {"role": "assistant", "content": "Python is a high-level programming language..."},
      {"role": "user", "content": "What are its main features?"}
    ],
    "model": "gemini-2.5-flash",
    "temperature": 0.7
  }'
```

**Request body**:
```json
{
  "messages": [
    {"role": "user", "content": "First message"},
    {"role": "assistant", "content": "Assistant's previous response"},
    {"role": "user", "content": "Follow-up question"}
  ],
  "model": "gemini-2.5-flash",  // Optional
  "temperature": 0.7  // Optional
}
```

**Response** (streaming):
```
Python's main features include: 1) Simple and readable syntax...
```

**Expected behavior**: Streams response while maintaining context from previous messages

---

### POST /api/chat/thinking

Generate response with thinking process for complex reasoning

**Example**:
```bash
curl -X POST http://localhost:8000/api/chat/thinking \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Solve this math problem: If a train travels 120km in 2 hours, then slows down to 40km/h for the next 3 hours, what is the total distance traveled?",
    "model": "gemini-3-pro-preview"
  }'
```

**Request body**:
```json
{
  "prompt": "Complex reasoning task or problem",
  "model": "gemini-3-pro-preview"  // Optional, defaults to gemini-3-pro-preview
}
```

**Response** (JSON):
```json
{
  "thinking": "First, I need to calculate the distance in the first segment...",
  "response": "The total distance traveled is 360 kilometers. Here's the breakdown: First 2 hours: 120km, Next 3 hours at 40km/h: 120km, Total: 240km"
}
```

**Expected behavior**: Returns both the model's thinking process and the final response

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (e.g., empty prompt)
- `500`: Server error (e.g., API key issues)

**Example error response**:
```json
{
  "detail": "Prompt cannot be empty"
}
```

## Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| General chat, Q&A | `gemini-2.5-flash` | Best price-performance |
| Complex reasoning, math, code | `gemini-2.5-pro` | Advanced thinking capabilities |
| Multimodal tasks (images, video) | `gemini-3-pro-preview` | Best multimodal understanding |
| High-volume, speed-critical | `gemini-2.5-flash-lite` | Fastest response time |

## Testing with Python

```python
import requests

# Simple streaming chat
response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={"prompt": "Hello, how are you?"},
    stream=True
)

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    print(chunk, end="", flush=True)

# Chat with history
response = requests.post(
    "http://localhost:8000/api/chat/history",
    json={
        "messages": [
            {"role": "user", "content": "What's Python?"},
            {"role": "assistant", "content": "Python is a programming language..."},
            {"role": "user", "content": "What are its benefits?"}
        ]
    },
    stream=True
)

# Complex reasoning
response = requests.post(
    "http://localhost:8000/api/chat/thinking",
    json={
        "prompt": "Explain the proof of Fermat's Last Theorem",
        "model": "gemini-2.5-pro"
    }
)
result = response.json()
print(f"Thinking: {result['thinking']}")
print(f"Response: {result['response']}")
```

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test all endpoints directly in your browser.

## Get Your Google API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API key"
3. Create a new API key or use an existing one
4. Copy the key to your `.env` file

## Project Structure

```
backend/
├── main.py              # FastAPI app with all endpoints
├── ai_assistant.py      # Gemini API integration
├── constants.py         # Settings and model constants
├── pyproject.toml       # Dependencies (managed with uv)
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment template
├── README.md            # Project overview
├── ref.md              # This API reference
└── tests/              # Unit tests
```

## Notes

- All streaming endpoints use `text/plain` media type
- The thinking endpoint returns JSON (non-streaming)
- Temperature range: 0.0 (deterministic) to 2.0 (creative)
- All models support 1M token context window
- Responses are streamed in real-time for better UX
