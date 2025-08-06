import axios from "axios";

const API_BASE = "http://localhost:8000";

export const translateText = async (text, fromLang, toLang) => {
  try {
    const res = await axios.post(`${API_BASE}/translate/translate`, {
      text,
      from: fromLang,
      to: toLang,
    });
    return res.data.translated_text;
  } catch (error) {
    console.error("Translation error:", error);
    return "Error translating text";
  }
};
