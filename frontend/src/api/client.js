/**
 * Centralized API client for Z-GPT frontend
 * Handles base URL configuration and request/response logic
 */
import axios from "axios";

// Get backend URL from environment variable or default to localhost
const BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

/**
 * Create axios instance with base configuration
 */
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Request interceptor for logging (in development)
 */
apiClient.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === "development") {
      console.log("API Request:", config.method.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === "development") {
      console.log("API Response:", response.status, response.data);
    }
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * API helper functions
 */
export const api = {
  /**
   * Send a chat message
   * @param {string} message - User message
   * @param {Array} history - Conversation history
   * @returns {Promise} Response data
   */
  sendChatMessage: async (message, history = []) => {
    const response = await apiClient.post("/chat/", { message, history });
    return response.data;
  },

  /**
   * Generate an image from prompt
   * @param {string} prompt - Image generation prompt
   * @param {number} guidanceScale - Optional guidance scale
   * @returns {Promise} Response data with base64 image
   */
  generateImage: async (prompt, guidanceScale = 8.5) => {
    const response = await apiClient.post("/image/generate", {
      prompt,
      guidance_scale: guidanceScale,
    });
    return response.data;
  },

  /**
   * Translate text between languages
   * @param {string} text - Text to translate
   * @param {string} fromLang - Source language code
   * @param {string} toLang - Target language code
   * @returns {Promise} Response data with translated text
   */
  translateText: async (text, fromLang = "en", toLang = "ur") => {
    const response = await apiClient.post("/translate/translate", {
      text,
      from: fromLang,
      to: toLang,
    });
    return response.data;
  },

  /**
   * Check backend health status
   * @returns {Promise} Health status
   */
  checkHealth: async () => {
    const response = await apiClient.get("/");
    return response.data;
  },
};

export default apiClient;
