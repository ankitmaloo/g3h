"""
Test Invisible Watermark - Roundtrip using kd.jpeg

Uses the existing kd.jpeg image to test:
1. Embed watermark with test string
2. Decode watermark via verify endpoint
3. Assert the strings match
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def kd_image_bytes():
    """Load the existing kd.jpeg test image."""
    kd_path = Path(__file__).parent.parent / "kd.jpeg"
    assert kd_path.exists(), f"Test image not found: {kd_path}"
    return kd_path.read_bytes()


class TestWatermarkRoundtrip:
    """Test watermark embedding and extraction roundtrip."""
    
    def test_embed_and_decode_roundtrip(self, client, kd_image_bytes):
        """
        Test full roundtrip:
        1. Watermark kd.jpeg with test string
        2. Send watermarked image to verify endpoint
        3. Check extracted string matches
        """
        test_payload = '{"VIP": true, "RefundLimit": 1000}'
        
        # Step 1: Generate image with watermark
        # Using the generate endpoint which embeds the watermark
        gen_response = client.post(
            "/api/generate-image",
            files=[("files", ("kd.jpeg", kd_image_bytes, "image/jpeg"))],
            data={"watermark_text": test_payload}
        )
        
        assert gen_response.status_code == 200, f"Generate failed: {gen_response.text}"
        gen_data = gen_response.json()
        assert gen_data["watermark_embedded"] is True
        
        # Decode the base64 image
        import base64
        watermarked_bytes = base64.b64decode(gen_data["image"])
        
        # Step 2: Send to verify endpoint to extract watermark
        verify_response = client.post(
            "/api/verify",
            files=[("file", ("watermarked.png", watermarked_bytes, "image/png"))]
        )
        
        assert verify_response.status_code == 200, f"Verify failed: {verify_response.text}"
        verify_data = verify_response.json()
        
        # Step 3: Assert the extracted data matches
        assert verify_data["verified"] is True
        assert verify_data["extracted_data"] is not None
        assert test_payload in verify_data["extracted_data"], \
            f"Expected '{test_payload}' in '{verify_data['extracted_data']}'"
    
    def test_no_watermark_image(self, client, kd_image_bytes):
        """Test that verifying an unwatermarked image returns no data."""
        # Send original kd.jpeg without watermarking
        verify_response = client.post(
            "/api/verify",
            files=[("file", ("kd.jpeg", kd_image_bytes, "image/jpeg"))]
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        # Original image should have no watermark (or garbage data)
        # Note: DCT decoder may return some noise, but it won't be valid JSON
        if verify_data["extracted_data"]:
            # If something is extracted, it shouldn't be our structured payload
            assert "VIP" not in verify_data["extracted_data"]


class TestWatermarkModule:
    """Unit tests for watermark module functions."""
    
    def test_embed_decode_direct(self, kd_image_bytes):
        """Test watermark functions directly without API."""
        from watermark import embed_watermark, decode_watermark
        
        test_text = "Hello, Hidden World!"
        
        # Embed watermark
        watermarked = embed_watermark(kd_image_bytes, test_text)
        assert watermarked is not None
        assert len(watermarked) > 0
        
        # Decode watermark
        decoded = decode_watermark(watermarked)
        assert decoded is not None
        assert test_text in decoded, f"Expected '{test_text}' in '{decoded}'"
    
    def test_json_payload(self, kd_image_bytes):
        """Test with JSON payload like production use."""
        from watermark import embed_watermark, decode_watermark
        
        payload = '{"user_id": "abc123", "tier": "premium"}'
        
        watermarked = embed_watermark(kd_image_bytes, payload)
        decoded = decode_watermark(watermarked)
        
        assert decoded is not None
        assert payload in decoded
