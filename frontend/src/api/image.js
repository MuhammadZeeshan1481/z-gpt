import axios from "axios";

const BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API_KEY = process.env.REACT_APP_API_KEY || "";  // Optional: Add your API key here or in .env

const getHeaders = () => {
  const headers = {
    "Content-Type": "application/json",
  };
  
  // Add API key if available
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  
  return headers;
};

export const generateImage = async (prompt) => {
  try {
    const res = await axios.post(
      `${BASE_URL}/image/generate`,
      { prompt },
      { headers: getHeaders() }
    );
    
    console.log("✓ Image generated successfully");
    
    // Log rate limit info if available
    if (res.headers['x-ratelimit-remaining']) {
      console.log(`Rate Limit: ${res.headers['x-ratelimit-remaining']}/${res.headers['x-ratelimit-limit']} remaining`);
    }
    
    return res.data.image_base64;
  } catch (err) {
    console.error("Image generation failed:", err);
    
    // Handle rate limit errors
    if (err.response?.status === 429) {
      const detail = err.response.data?.detail;
      throw new Error(detail?.message || "Rate limit exceeded. Please wait and try again.");
    }
    
    // Handle auth errors
    if (err.response?.status === 401) {
      throw new Error("Authentication required. Please configure your API key.");
    }
    
    throw err;
  }
};
