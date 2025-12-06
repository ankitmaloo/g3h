# Testing Patterns

## Unit Test Structure

Always create unit tests before implementing non-AI features. Use subagents to:
1. Write unit tests first
2. Run tests to verify implementation

### Basic Test Pattern

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_hello_world():
    """Test hello world endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
```

### Testing Streaming Endpoints

```python
def test_stream_endpoint():
    """Test streaming endpoint"""
    with client.stream("GET", "/stream") as response:
        assert response.status_code == 200
        chunks = []
        for chunk in response.iter_text():
            chunks.append(chunk)
        assert len(chunks) > 0
```

### Testing with Environment Variables

```python
import os
from unittest.mock import patch

@patch.dict(os.environ, {"API_KEY": "test_key"})
def test_with_env():
    """Test with mocked environment variables"""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

## Test Organization

- `tests/test_main.py` - Test main endpoints
- `tests/test_ai_assistant.py` - Test AI functionality
- `tests/test_firebase.py` - Test Firebase integration
- etc.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_health_check
```
