/**
 * API Service for backend communication
 */

const API_BASE = "http://localhost:8000";

export interface GenerateImageResponse {
    image: string;
    mock_mode: boolean;
    watermark_embedded: boolean;
}

/**
 * Generate image from reference images with optional watermark
 * @param files - Array of reference image files (max 5)
 * @param watermarkText - Optional text to embed invisibly
 * @returns Promise with base64 data URL of generated image
 */
export async function generateImage(files: File[], watermarkText?: string): Promise<string> {
    if (files.length === 0) {
        throw new Error("At least one reference image is required");
    }

    if (files.length > 5) {
        throw new Error("Maximum 5 reference images allowed");
    }

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    // Add watermark text if provided
    if (watermarkText && watermarkText.trim()) {
        formData.append("watermark_text", watermarkText);
    }

    const response = await fetch(`${API_BASE}/api/generate-image`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `Generation failed: ${response.statusText}`);
    }

    const data: GenerateImageResponse = await response.json();

    // Log if in mock mode
    if (data.mock_mode) {
        console.log("[API] Backend is in mock mode - returning reference image");
    }
    if (data.watermark_embedded) {
        console.log("[API] Watermark embedded successfully");
    }

    return `data:image/png;base64,${data.image}`;
}

/**
 * Health check for backend
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

export interface VerifyImageResponse {
    analysis: string;
    verified: boolean;
    extracted_data: string | null;
    mock_mode: boolean;
}

/**
 * Verify/analyze an image for embedded data or authenticity
 * @param file - Image file to verify
 * @returns Promise with analysis text result
 */
export async function verifyImage(file: File): Promise<VerifyImageResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/api/verify`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `Verification failed: ${response.statusText}`);
    }

    const data: VerifyImageResponse = await response.json();

    if (data.mock_mode) {
        console.log("[API] Backend is in mock mode - returning placeholder analysis");
    }

    return data;
}
