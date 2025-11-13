import { api } from "./client";

/**
 * Generate an image from a text prompt
 * @param {string} prompt - Text prompt for image generation
 * @param {number} guidanceScale - Optional guidance scale
 * @returns {Promise<string>} Base64 encoded image
 */
export const generateImage = async (prompt, guidanceScale = 8.5) => {
  try {
    const response = await api.generateImage(prompt, guidanceScale);
    return response.image_base64;
  } catch (err) {
    console.error("Image generation failed:", err);
    throw err;
  }
};
