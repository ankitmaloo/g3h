# Gemini AI Backend

FastAPI backend with the latest Google Gemini models (2025), including Gemini 3 Pro, Gemini 2.5 Pro, and Gemini 2.5 Flash.

## Features

- **Latest Gemini Models**: Gemini 3 Pro, 2.5 Pro, 2.5 Flash, 2.5 Flash Lite
- **Streaming Responses**: Real-time text streaming for better UX
- **Conversation History**: Maintain context across multiple messages
- **Thinking Mode**: Advanced reasoning with Gemini 3 Pro
- **Built with uv**: Fast, modern Python package management
- **FastAPI**: High-performance async API framework
- **CORS Enabled**: Ready for frontend integration

## Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-3-pro-preview` | Best multimodal understanding | Complex tasks with text, images, video, audio |
| `gemini-2.5-pro` | State-of-the-art thinking | Complex reasoning, code, math, STEM |
| `gemini-2.5-flash` | Strong price-performance (default) | General chat, high-volume tasks |
| `gemini-2.5-flash-lite` | Fastest, cost-efficient | Speed-critical applications |

All models support 1M token context window.

## Quick Start

1. **Get Google API Key**

   Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and create an API key.

2. **Setup Environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Install Dependencies**

   ```bash
   uv sync
   ```

4. **Run the Server**

   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```

5. **Test the API**

   ```bash
   curl -X POST http://localhost:8000/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, explain quantum computing"}'
   ```

## API Endpoints

- `GET /` - Hello World
- `GET /health` - Health check
- `GET /api/models` - List available models
- `POST /api/chat/stream` - Stream chat response
- `POST /api/chat/history` - Chat with conversation history
- `POST /api/chat/thinking` - Complex reasoning with thinking process

See [ref.md](./ref.md) for complete API documentation with examples.

## Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI app with all endpoints
├── ai_assistant.py      # Gemini API integration functions
├── constants.py         # Settings and model constants
├── pyproject.toml       # Dependencies (uv managed)
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment template
├── README.md            # This file
├── ref.md              # Detailed API reference
└── tests/              # Unit tests
```

## Testing

Run tests:
```bash
uv run pytest
```

With coverage:
```bash
uv run pytest --cov=. --cov-report=html
```

## Development

The project uses:
- **uv**: Modern Python package manager (faster than pip)
- **FastAPI**: Async web framework
- **google-generativeai**: Official Gemini API client
- **Pydantic**: Data validation and settings

## License

MIT
