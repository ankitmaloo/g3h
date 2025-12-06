# Gemini API Patterns

## Official Resources

Before implementing any Gemini functionality, consult these official cookbooks:

- **Thinking/Reasoning**: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb
- **Live API with Tools**: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI_tools.ipynb
- **Search Grounding**: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Search_Grounding.ipynb
- **Image Generation**: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Image_out.ipynb

## Streaming Pattern

Always use streaming for text responses. For images and other modalities, send data at the end.

### Text Streaming Example

```python
import google.generativeai as genai

async def stream_gemini_response(prompt: str):
    """Stream text response from Gemini"""
    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
    
    response = model.generate_content(
        prompt,
        stream=True
    )
    
    for chunk in response:
        if chunk.text:
            yield chunk.text
```

### Image Response Pattern

```python
async def generate_image_response(prompt: str):
    """Generate image with Gemini, send at end"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    response = model.generate_content(prompt)
    
    # Extract image data
    image_data = None
    for part in response.parts:
        if hasattr(part, 'inline_data'):
            image_data = part.inline_data.data
            break
    
    return {
        "text": response.text if response.text else "",
        "image": image_data
    }
```

## Implementation Process

1. Search for the specific cookbook/API reference
2. Get the exact format and method signatures
3. Implement using the official pattern
4. Add streaming where applicable
