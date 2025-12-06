
import os
import sys
from watermark import embed_watermark, decode_watermark

def test_config(name, method, **kwargs):
    print(f"\n====== Testing Config: {name} ({method}) ======")
    # 1. Load source
    if os.path.exists("kd.jpeg"):
        with open("kd.jpeg", "rb") as f: source_bytes = f.read()
    else:
        return # Should exist
        
    payload = "Test Watermark 123"
    payload_bytes = payload.encode('utf-8')
    MAX_PAYLOAD_BYTES = 252
    length_prefix = struct.pack('>H', len(payload_bytes))
    padded_payload = payload_bytes.ljust(MAX_PAYLOAD_BYTES, b'\x00')
    full_data = length_prefix + padded_payload
    
    # Embed
    from PIL import Image
    import io
    import cv2
    import numpy as np
    from imwatermark import WatermarkEncoder, WatermarkDecoder
    
    pil_image = Image.open(io.BytesIO(source_bytes)).convert('RGB')
    bgr_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    encoder = WatermarkEncoder()
    encoder.set_watermark('bytes', full_data)
    
    try:
        watermarked_bgr = encoder.encode(bgr_image, method, **kwargs)
    except Exception as e:
        print(f"Encoding failed: {e}")
        return

    watermarked_rgb = cv2.cvtColor(watermarked_bgr, cv2.COLOR_BGR2RGB)
    out_buf = io.BytesIO()
    Image.fromarray(watermarked_rgb).save(out_buf, format='PNG')
    watermarked_bytes = out_buf.getvalue()
    
    # Helper to decode
    def try_decode(img_bytes, desc):
        try:
            pil = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            decoder = WatermarkDecoder('bytes', 254 * 8)
            wm_bytes = decoder.decode(bgr, method)
            if wm_bytes and len(wm_bytes) >= 2:
                plen = struct.unpack('>H', wm_bytes[:2])[0]
                if plen > 252: return f"Invalid len {plen}"
                return wm_bytes[2:2+plen].decode('utf-8', errors='ignore')
            return "None"
        except Exception as e:
            return f"Error: {e}"

    # Results
    # 1. Direct
    res_direct = try_decode(watermarked_bytes, "Direct")
    success_direct = (res_direct == payload)
    
    # 2. JPEG
    img = Image.open(io.BytesIO(watermarked_bytes))
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    jpeg_bytes = buf.getvalue()
    res_jpeg = try_decode(jpeg_bytes, "JPEG")
    success_jpeg = (res_jpeg == payload)
    
    # 3. Resize 90%
    w, h = img.size
    img_res = img.resize((int(w*0.9), int(h*0.9)), Image.LANCZOS)
    buf = io.BytesIO()
    img_res.save(buf, format='PNG')
    res_bytes = buf.getvalue()
    res_resize = try_decode(res_bytes, "Resize")
    success_resize = (res_resize == payload)
    
    print(f"Direct: {res_direct} [{'PASS' if success_direct else 'FAIL'}]")
    print(f"JPEG:   {res_jpeg} [{'PASS' if success_jpeg else 'FAIL'}]")
    print(f"Resize: {res_resize} [{'PASS' if success_resize else 'FAIL'}]")


if __name__ == "__main__":
    # Test Default
    test_config("Default dwtDct", 'dwtDct')
    
    # Test Stronger Scales
    # Default is approx [0, 136, 0, 0]?
    test_config("Stronger scales=[0, 170, 0, 0]", 'dwtDct', scales=[0, 170, 0, 0])
    
    # Test dwtDctSvd if available
    try:
        test_config("dwtDctSvd Default", 'dwtDctSvd')
    except:
        print("dwtDctSvd not supported")


