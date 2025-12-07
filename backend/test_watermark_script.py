#!/usr/bin/env python3
"""
Test script to:
1. Load kd.jpeg image
2. Embed watermark "texting the watermark" 
3. Save as kd_w.jpeg
4. Test verify endpoint with watermarked image
"""

import sys
import os
import requests

# Add backend to path to import watermark module
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from watermark import embed_watermark

# Configuration
BACKEND_URL = "http://localhost:8000"
KD_JPEG_PATH = "/Users/ankit/Documents/dev/hacks/g3/backend/kd.jpeg"
KD_W_JPEG_PATH = "/Users/ankit/Documents/dev/hacks/g3/kd_w.jpeg"
WATERMARK_TEXT = "texting the watermark"

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def load_and_embed_watermark():
    """Load kd.jpeg and embed watermark"""
    try:
        # Read the original image
        with open(KD_JPEG_PATH, 'rb') as f:
            original_image_bytes = f.read()
        
        print(f"📖 Loaded kd.jpeg ({len(original_image_bytes)} bytes)")
        
        # Embed watermark
        print(f"🔒 Embedding watermark: '{WATERMARK_TEXT}'")
        watermarked_bytes = embed_watermark(original_image_bytes, WATERMARK_TEXT)
        
        print(f"🔒 Watermark embedded ({len(watermarked_bytes)} bytes)")
        
        # Save watermarked image
        with open(KD_W_JPEG_PATH, 'wb') as f:
            f.write(watermarked_bytes)
        
        print(f"💾 Saved watermarked image to kd_w.jpeg")
        return True
        
    except Exception as e:
        print(f"❌ Error embedding watermark: {e}")
        return False

def test_verify_endpoint():
    """Test the verify endpoint with watermarked image"""
    try:
        # Open and read the watermarked image
        with open(KD_W_JPEG_PATH, 'rb') as f:
            watermarked_image_bytes = f.read()
        
        print(f"📖 Loaded kd_w.jpeg for verification ({len(watermarked_image_bytes)} bytes)")
        
        # Send to verify endpoint
        files = {'file': ('kd_w.jpeg', watermarked_image_bytes, 'image/jpeg')}
        response = requests.post(f"{BACKEND_URL}/api/verify", files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Verify endpoint response:")
            print(f"   - Verified: {result['verified']}")
            print(f"   - Mock mode: {result['mock_mode']}")
            
            if result['verified']:
                extracted_data = result.get('extracted_data', '')
                print(f"   - Extracted watermark: '{extracted_data}'")
                print(f"   - Expected watermark: '{WATERMARK_TEXT}'")
                
                if extracted_data == WATERMARK_TEXT:
                    print("🎉 SUCCESS: Watermark correctly detected and verified!")
                    return True
                else:
                    print("⚠️  WARNING: Watermark detected but text doesn't match expected")
                    return False
            else:
                print("❌ FAILURE: Watermark not detected")
                return False
        else:
            print(f"❌ Verify endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing verify endpoint: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Starting watermark test script...")
    print(f"📁 Backend URL: {BACKEND_URL}")
    print(f"📁 Original image: {KD_JPEG_PATH}")
    print(f"📁 Watermarked image: {KD_W_JPEG_PATH}")
    print()
    
    # Task Progress Checklist
    task_progress = [
        "Check if backend is running",
        "Load kd.jpeg image", 
        "Call embed_watermark with 'texting the watermark'",
        "Save result as kd_w.jpeg",
        "Test verify endpoint with watermarked image",
        "Print results and verification status"
    ]
    
    results = []
    
    # Step 1: Check backend
    print("1️⃣ Checking backend status...")
    backend_running = check_backend_status()
    results.append(("Backend status", backend_running))
    
    if not backend_running:
        print("❌ Cannot proceed without backend running")
        return
    
    print()
    
    # Step 2-4: Load, embed, and save watermark
    print("2️⃣ Loading and embedding watermark...")
    embed_success = load_and_embed_watermark()
    results.append(("Embed watermark", embed_success))
    
    if not embed_success:
        print("❌ Cannot proceed with failed embedding")
        return
    
    print()
    
    # Step 5-6: Test verify endpoint
    print("3️⃣ Testing verify endpoint...")
    verify_success = test_verify_endpoint()
    results.append(("Verify endpoint", verify_success))
    
    print()
    print("📊 SUMMARY:")
    print("=" * 50)
    for task, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{task:<25} {status}")
    
    all_passed = all(success for _, success in results)
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED!")
    
    print()
    print("📁 Files created:")
    print(f"   - {KD_W_JPEG_PATH}")
    print(f"   - Contains watermark: '{WATERMARK_TEXT}'")

if __name__ == "__main__":
    main()
