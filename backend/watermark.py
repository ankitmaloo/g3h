"""
Invisible Watermark Module
Uses DCT (Discrete Cosine Transform) frequency domain analysis to embed/extract hidden data.

The invisible-watermark library uses the dwtDct method which:
1. Transforms image to frequency domain using DWT (Discrete Wavelet Transform)
2. Applies DCT (Discrete Cosine Transform) to embed data
3. Modifies high-frequency components (invisible to humans)
4. Data survives compression, resizing, and minor edits

Encoding format: First 2 bytes = payload length (big endian), then payload bytes.
This allows decoder to know how many bytes to extract.
"""

import io
import struct
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from imwatermark import WatermarkEncoder, WatermarkDecoder

# Maximum payload size in bytes (252 bytes for data + 2 bytes for length = 254 total)
# This gives us 2032 bits which the library can handle
MAX_PAYLOAD_BYTES = 252


def embed_watermark(image_bytes: bytes, payload: str) -> bytes:
    """
    Embed invisible watermark into image using DCT frequency domain.
    
    Args:
        image_bytes: Input image as bytes
        payload: Text string to hide in the image (max 252 bytes)
    
    Returns:
        Watermarked image as PNG bytes
    """
    payload_bytes = payload.encode('utf-8')
    
    if len(payload_bytes) > MAX_PAYLOAD_BYTES:
        raise ValueError(f"Payload too large: {len(payload_bytes)} bytes, max {MAX_PAYLOAD_BYTES}")
    
    # Create length-prefixed data: 2 bytes length + payload + padding
    length_prefix = struct.pack('>H', len(payload_bytes))  # Big-endian unsigned short
    
    # Pad to fixed size for consistent decoding
    padded_payload = payload_bytes.ljust(MAX_PAYLOAD_BYTES, b'\x00')
    full_data = length_prefix + padded_payload  # Always 254 bytes
    
    # Convert bytes to numpy array via PIL
    pil_image = Image.open(io.BytesIO(image_bytes))
    
    # Ensure RGB mode (watermark library requires RGB)
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to OpenCV format (BGR)
    img_array = np.array(pil_image)
    bgr_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Encode watermark using dwtDct method (robust DCT-based)
    encoder = WatermarkEncoder()
    encoder.set_watermark('bytes', full_data)
    watermarked_bgr = encoder.encode(bgr_image, 'dwtDct')
    
    # Convert back to RGB and then to bytes
    watermarked_rgb = cv2.cvtColor(watermarked_bgr, cv2.COLOR_BGR2RGB)
    watermarked_pil = Image.fromarray(watermarked_rgb)
    
    output = io.BytesIO()
    watermarked_pil.save(output, format='PNG')
    return output.getvalue()


def decode_watermark(image_bytes: bytes) -> Optional[str]:
    """
    Extract hidden watermark from image using DCT frequency domain analysis.
    
    The decoder looks at high-frequency components in the image where
    the watermark data was encoded as a specific mathematical pattern.
    
    Args:
        image_bytes: Image bytes to analyze
    
    Returns:
        Extracted text string, or None if no watermark found
    """
    try:
        # Convert bytes to numpy array via PIL
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Ensure RGB mode
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to OpenCV format (BGR)
        img_array = np.array(pil_image)
        bgr_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Decode watermark - we know it's 254 bytes (2 + 252) = 2032 bits
        total_bytes = 2 + MAX_PAYLOAD_BYTES  # 254
        decoder = WatermarkDecoder('bytes', total_bytes * 8)  # Bits, not bytes
        watermark_bytes = decoder.decode(bgr_image, 'dwtDct')
        
        if watermark_bytes and len(watermark_bytes) >= 2:
            # Extract length from first 2 bytes
            payload_length = struct.unpack('>H', watermark_bytes[:2])[0]
            
            # Sanity check: length must be reasonable
            if payload_length > MAX_PAYLOAD_BYTES:
                # 65535 (0xFFFF) is common for non-watermarked images (all 1s)
                if payload_length != 65535:
                    print(f"[Watermark] Invalid length extracted: {payload_length}")
                return None
            
            # Extract actual payload
            payload_bytes = watermark_bytes[2:2 + payload_length]
            text = payload_bytes.decode('utf-8', errors='ignore')
            return text if text else None
        
        return None
        
    except Exception as e:
        print(f"[Watermark] Decode error: {e}")
        return None
