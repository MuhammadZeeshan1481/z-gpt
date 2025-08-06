import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const generateImage = async (prompt) => {
  try {
    const res = await axios.post(`${BASE_URL}/image/generate`, { prompt });
    return res.data.image_base64;
  } catch (err) {
    console.error("Image generation failed:", err);
    throw err;
  }
};
