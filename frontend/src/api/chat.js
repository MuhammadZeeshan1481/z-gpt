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

export const sendMessage = async (message, history = []) => {
  try {
    const response = await axios.post(
      `${BASE_URL}/chat/`,
      { message, history },
      { headers: getHeaders() }
    );
    console.log("✓ Backend Response:", response.data);
    
    // Log rate limit info if available
    if (response.headers['x-ratelimit-remaining']) {
      console.log(`Rate Limit: ${response.headers['x-ratelimit-remaining']}/${response.headers['x-ratelimit-limit']} remaining`);
    }
    
    return response.data;
  } catch (err) {
    console.error("Chat API error:", err);
    
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
