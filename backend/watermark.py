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
from collections import Counter
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from imwatermark import WatermarkEncoder, WatermarkDecoder

# Preferred watermark methods and tunable scales
PRIMARY_METHOD = 'dwtDctSvd'  # more robust variant if available
FALLBACK_METHOD = 'dwtDct'
PRIMARY_SCALES = [0, 40, 0, 0]  # slightly stronger to survive resampling/screenshotting
FALLBACK_SCALES = [0, 220, 0, 0]  # slightly stronger to reduce corruption

# Redundancy: tile the frame so each region carries the payload
TILE_GRIDS = [(3, 3), (2, 2)]  # pick the largest grid that fits
MIN_TILE_DIM = 512  # avoid tiles that are too small for the algorithm

# Encoding/saving defaults
JPEG_QUALITY = 97  # keep JPEG high quality so the signal survives

# Fixed-length payload: 512 bytes + 2-byte length prefix = 514 bytes total
# Shorter payloads are padded with nulls; longer payloads are rejected
MAX_PAYLOAD_BYTES = 512


def detect_mime(image_bytes: bytes) -> str:
    """Simple mime detection from magic bytes."""
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if image_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    if image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    return "image/png"


def embed_watermark(image_bytes: bytes, payload: str, output_format: Optional[str] = None) -> bytes:
    """
    Embed invisible watermark into image using DCT frequency domain.
    
    Args:
        image_bytes: Input image as bytes
        payload: Text string to hide in the image (max 512 bytes)
        output_format: Optional override for output format (e.g., 'JPEG', 'PNG', 'WEBP')
    
    Returns:
        Watermarked image bytes in the chosen format
    """
    payload_bytes = payload.encode('utf-8')
    
    if len(payload_bytes) > MAX_PAYLOAD_BYTES:
        raise ValueError(f"Payload too large: {len(payload_bytes)} bytes, max {MAX_PAYLOAD_BYTES}")
    
    # Create length-prefixed data: 2 bytes length + payload + padding
    length_prefix = struct.pack('>H', len(payload_bytes))  # Big-endian unsigned short
    
    # Pad to fixed size for consistent decoding (always fixed payload)
    padded_payload = payload_bytes.ljust(MAX_PAYLOAD_BYTES, b'\x00')
    full_data = length_prefix + padded_payload  # Always length + payload
    
    # Convert bytes to numpy array via PIL
    pil_image = Image.open(io.BytesIO(image_bytes))
    
    # Ensure RGB mode (watermark library requires RGB)
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to OpenCV format (BGR)
    img_array = np.array(pil_image)
    bgr_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    def _encode_section(section: np.ndarray) -> np.ndarray:
        """Encode the payload into a single image/tile."""
        encoder = WatermarkEncoder()
        encoder.set_watermark('bytes', full_data)
        try:
            return encoder.encode(section, PRIMARY_METHOD, scales=PRIMARY_SCALES)
        except TypeError:
            # Scales not supported for this method; retry without them
            pass
        except Exception:
            pass
        try:
            return encoder.encode(section, PRIMARY_METHOD)
        except Exception:
            pass
        try:
            return encoder.encode(section, FALLBACK_METHOD, scales=FALLBACK_SCALES)
        except Exception as exc:
            raise RuntimeError("Watermark encoding failed for primary and fallback methods") from exc

    # Choose the largest tiling grid that fits; fall back to whole-frame encoding
    h, w = bgr_image.shape[:2]
    grid = None
    for candidate in TILE_GRIDS:
        rows, cols = candidate
        if h >= rows * MIN_TILE_DIM and w >= cols * MIN_TILE_DIM:
            grid = candidate
            break

    watermarked_bgr = bgr_image.copy()
    if grid:
        rows, cols = grid
        tile_h = h // rows
        tile_w = w // cols
        for r in range(rows):
            for c in range(cols):
                y0 = r * tile_h
                y1 = h if r == rows - 1 else (r + 1) * tile_h
                x0 = c * tile_w
                x1 = w if c == cols - 1 else (c + 1) * tile_w
                watermarked_bgr[y0:y1, x0:x1] = _encode_section(watermarked_bgr[y0:y1, x0:x1])
    else:
        watermarked_bgr = _encode_section(watermarked_bgr)
    
    # Convert back to RGB and then to bytes
    watermarked_rgb = cv2.cvtColor(watermarked_bgr, cv2.COLOR_BGR2RGB)
    watermarked_pil = Image.fromarray(watermarked_rgb)
    
    # Decide output format: prefer provided, else source format, else PNG
    fmt = (output_format or pil_image.format or detect_mime(image_bytes) or "PNG").upper()
    if fmt == "JPG":
        fmt = "JPEG"
    output = io.BytesIO()
    save_kwargs = {}
    if fmt == "JPEG":
        save_kwargs = {"quality": JPEG_QUALITY, "optimize": True, "subsampling": 0}
    watermarked_pil.save(output, format=fmt, **save_kwargs)
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
        
        def _try_decode(section: np.ndarray, method: str) -> Optional[str]:
            total_bytes = 2 + MAX_PAYLOAD_BYTES  # fixed length
            decoder = WatermarkDecoder('bytes', total_bytes * 8)  # Bits, not bytes
            watermark_bytes = decoder.decode(section, method)
            if watermark_bytes and len(watermark_bytes) >= 2:
                payload_length = struct.unpack('>H', watermark_bytes[:2])[0]
                if payload_length > MAX_PAYLOAD_BYTES:
                    if payload_length != 65535:
                        print(f"[Watermark] Invalid length extracted: {payload_length} ({method})")
                    return None
                payload_bytes = watermark_bytes[2:2 + payload_length]
                text = payload_bytes.decode('utf-8', errors='ignore')
                return text if text else None
            return None

        def decode_section(section: np.ndarray) -> Optional[str]:
            text = _try_decode(section, PRIMARY_METHOD)
            if not text:
                text = _try_decode(section, FALLBACK_METHOD)
            return text

        candidates = []

        # Whole-frame decode
        text = decode_section(bgr_image)
        if text:
            candidates.append(text)

        # Tile-aware decode for redundancy/majority vote
        h, w = bgr_image.shape[:2]
        grid = None
        for candidate in TILE_GRIDS:
            rows, cols = candidate
            if h >= rows * MIN_TILE_DIM and w >= cols * MIN_TILE_DIM:
                grid = candidate
                break
        if grid:
            rows, cols = grid
            tile_h = h // rows
            tile_w = w // cols
            for r in range(rows):
                for c in range(cols):
                    y0 = r * tile_h
                    y1 = h if r == rows - 1 else (r + 1) * tile_h
                    x0 = c * tile_w
                    x1 = w if c == cols - 1 else (c + 1) * tile_w
                    tile_text = decode_section(bgr_image[y0:y1, x0:x1])
                    if tile_text:
                        candidates.append(tile_text)

        if not candidates:
            return None
        # Majority vote across tiles/full frame to survive partial corruption
        best_text, _ = Counter(candidates).most_common(1)[0]
        return best_text
        
    except Exception as e:
        print(f"[Watermark] Decode error: {e}")
        return None
