# OpenAI API Patterns

## Official Resources

Before implementing any OpenAI functionality, consult these official cookbooks:

- **Responses API with Reasoning**: https://github.com/openai/openai-cookbook/blob/main/examples/responses_api/reasoning_items.ipynb
- **Responses API with Tools**: https://github.com/openai/openai-cookbook/blob/main/examples/responses_api/responses_example.ipynb

## Streaming Pattern

Always use streaming for text responses.

### Text Streaming Example

```python
from openai import OpenAI

async def stream_openai_response(prompt: str, use_reasoning: bool = False):
    """Stream text response from OpenAI"""
    client = OpenAI()
    
    model = "o1" if use_reasoning else "gpt-4-turbo"
    
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Reasoning Response Pattern

```python
async def generate_reasoning_response(prompt: str):
    """Generate response with reasoning using o1"""
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="o1",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "content": response.choices[0].message.content,
        "reasoning": response.choices[0].message.get("reasoning", "")
    }
```

## Implementation Process

1. Search for the specific cookbook/API reference
2. Get the exact format and method signatures
3. Implement using the official pattern
4. Add streaming where applicable
