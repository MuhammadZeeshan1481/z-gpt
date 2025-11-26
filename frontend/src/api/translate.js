import { requestJson } from "./client";

export const translateText = async (text, fromLang, toLang) => {
  const res = await requestJson(`/translate/translate`, {
    method: "POST",
    body: JSON.stringify({ text, from: fromLang, to: toLang }),
  });
  return res.translated_text;
};
