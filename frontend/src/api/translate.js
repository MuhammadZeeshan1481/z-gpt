import { api } from "./client";

/**
 * Translate text between languages
 * @param {string} text - Text to translate
 * @param {string} fromLang - Source language code
 * @param {string} toLang - Target language code
 * @returns {Promise<string>} Translated text
 */
export const translateText = async (text, fromLang, toLang) => {
  try {
    const response = await api.translateText(text, fromLang, toLang);
    return response.translated_text;
  } catch (error) {
    console.error("Translation error:", error);
    return "Error translating text";
  }
};
