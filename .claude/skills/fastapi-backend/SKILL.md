---
name: fastapi-backend
description: FastAPI backend development with uv, CORS, environment variables, and AI model integrations (Gemini, OpenAI). Use when building or modifying FastAPI backends, implementing API endpoints, integrating AI models (Gemini with thinking/tools/search/images, OpenAI with reasoning/tools), adding streaming responses, working with Firebase, or creating backend services with proper testing and progressive development.
---

# FastAPI Backend Development

Build FastAPI backends with uv, proper structure, AI integrations, and streaming support.

## Project Initialization

For new projects, run the initialization script:

```bash
python scripts/init_project.py <project-name> [target-directory]
```

This creates:
- `main.py` with FastAPI app, CORS, hello world, health check
- `pyproject.toml` with uv configuration
- `.env.example` for environment variables
- `constants.py` for settings management
- `tests/` directory
- `.gitignore` and `README.md`

## File Structure Philosophy

Keep files simple and organized:

```
project/
├── main.py              # All endpoints (keep them here)
├── constants.py         # Settings and constants
├── ai_assistant.py      # AI model calls (if needed)
├── firebase.py          # Firebase integration (if needed)
├── [feature].py         # Other feature-specific files
├── pyproject.toml       # uv dependencies
├── .env                 # Environment variables (not committed)
└── tests/               # Unit tests
    ├── test_main.py
    └── test_[feature].py
```

**Key principle**: One main file with all endpoints, then separate files per feature/integration.

## Development Workflow

### 1. Plan Before Implementation

**CRITICAL**: Build progressively. Plan in stages:
- Stage 1: Core functionality (base endpoints)
- Stage 2: First feature (simplest integration)
- Stage 3: Additional features (one at a time)

Never try to one-shot complex implementations. Break them down.

### 2. Use Subagents Strategically

Use up to 10 subagents for different responsibilities:

**For AI Model Implementation**:
1. **Search subagent**: Fetch official cookbook/API reference
2. **Implementation subagent**: Write the integration code
3. **Validation subagent**: Review against official patterns

**For Non-AI Features**:
1. **Test writer subagent**: Write unit tests FIRST
2. **Implementation subagent**: Implement the feature
3. **Test runner subagent**: Run tests to verify

**For File Management**:
- Assign 1 subagent per file (main.py, ai_assistant.py, etc.)
- Main model validates all subagent changes

### 3. AI Model Integration Process

**Step 1: Search for Official Documentation**

Before implementing ANY AI model feature:

```bash
# Search for the specific cookbook
web_search: "gemini api thinking cookbook"
web_search: "openai responses api reasoning"
```

**Step 2: Fetch and Review**

```bash
# Get the exact format
web_fetch: [cookbook URL]
```

**Step 3: Implement Using Official Pattern**

Consult these references:
- `references/gemini_patterns.md` - Gemini API patterns
- `references/openai_patterns.md` - OpenAI API patterns

**Official Resources** (fetch at runtime):
- Gemini Thinking: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb
- Gemini Live Tools: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI_tools.ipynb
- Gemini Search: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Search_Grounding.ipynb
- Gemini Image Gen: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Image_out.ipynb
- OpenAI Reasoning: https://github.com/openai/openai-cookbook/blob/main/examples/responses_api/reasoning_items.ipynb
- OpenAI Tools: https://github.com/openai/openai-cookbook/blob/main/examples/responses_api/responses_example.ipynb

### 4. Always Use Streaming

**Text streaming**: Stream chunks as they arrive
**Images/other modalities**: Send data at the end

Example streaming endpoint structure:

```python
from fastapi.responses import StreamingResponse

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat responses"""
    async def generate():
        async for chunk in ai_assistant.stream_response(request.message):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")
```

### 5. Testing Requirements

**For non-AI features**: ALWAYS write tests first

Consult `references/testing_patterns.md` for patterns.

Process:
1. Subagent writes unit tests
2. Subagent implements feature
3. Subagent runs tests: `uv run pytest`
4. Main model validates all changes

### 6. API Documentation

For EVERY endpoint created, add an example to `ref.md`:

```markdown
## POST /api/chat

Stream chat response

**Example**:
\`\`\`bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
\`\`\`

**Response** (streaming):
\`\`\`
Hello! I'm doing well, thank you for asking...
\`\`\`

**Expected behavior**: Streams text chunks in real-time
```

Include:
- Endpoint path and method
- Request format (curl example)
- Response format (with example data)
- Expected values/behavior notes

## Environment Variables

Always use pydantic-settings for configuration (see `constants.py`):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    google_api_key: str = ""
    
    class Config:
        env_file = ".env"
```

Never hardcode API keys or sensitive values.

## Common Patterns

### Add AI Model Integration

1. Add dependency to pyproject.toml:
```bash
uv add openai google-generativeai
```

2. Create `ai_assistant.py`:
```python
from openai import OpenAI
from constants import settings

client = OpenAI(api_key=settings.openai_api_key)

async def stream_response(message: str):
    """Stream response from OpenAI"""
    stream = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

3. Add endpoint in `main.py`:
```python
from ai_assistant import stream_response

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.message),
        media_type="text/plain"
    )
```

### Add Firebase Integration

1. Add dependency:
```bash
uv add firebase-admin
```

2. Create `firebase.py`:
```python
import firebase_admin
from firebase_admin import credentials, firestore
from constants import settings

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": settings.firebase_project_id,
    # ... other fields from settings
})

firebase_admin.initialize_app(cred)
db = firestore.client()
```

3. Use in endpoints:
```python
from firebase import db

@app.get("/api/data")
async def get_data():
    docs = db.collection('items').stream()
    return [doc.to_dict() for doc in docs]
```

## Critical Reminders

1. **Build progressively**: Start small, add complexity incrementally
2. **Use subagents**: Delegate file-specific work, validate changes
3. **Search first**: For AI models, always get official docs before implementing
4. **Stream everything**: Text streams in chunks, images at end
5. **Test non-AI features**: Write tests first, run them
6. **Document endpoints**: Add curl examples to ref.md
7. **No unnecessary changes**: Only modify what's needed
8. **Validate everything**: Main model reviews all subagent work
9. **Don't run the server**: Assume it's running or ask user to run in venv
10. **Follow instructions**: Missing requirements reduces quality

## Dependency Management with uv

```bash
# Add package
uv add package-name

# Add dev dependency
uv add --dev pytest

# Sync dependencies
uv sync

# Run command
uv run uvicorn main:app --reload

# Run tests
uv run pytest
```

## Server Execution

Do NOT try to run the server. Assume it's already running, or instruct user:

```bash
# User should run:
uv run uvicorn main:app --reload --port 8000
```
