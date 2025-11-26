import { requestJson } from "./client";

export const generateImage = async (prompt) => {
  const res = await requestJson(`/image/generate`, {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
  return res.image_base64;
};
