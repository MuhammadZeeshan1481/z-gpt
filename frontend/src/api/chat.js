import { api } from "./client";

/**
 * Send a chat message
 * @param {string} message - User message
 * @param {Array} history - Conversation history
 * @returns {Promise} Response data
 */
export const sendMessage = async (message, history = []) => {
  try {
    return await api.sendChatMessage(message, history);
  } catch (err) {
    console.error("Chat API error:", err);
    throw err;
  }
};
