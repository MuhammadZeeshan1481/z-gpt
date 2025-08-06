import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const sendMessage = async (message, history = []) => {
  try {
    const response = await axios.post(`${BASE_URL}/chat/`, {
      message,
      history,
    });
    console.log(" Backend Response:", response.data);
    return response.data;
  } catch (err) {
    console.error("Chat API error:", err);
    throw err;
  }
};
