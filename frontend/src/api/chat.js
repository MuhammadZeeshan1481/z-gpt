import { requestJson } from "./client";

const buildPayload = ({ message, sessionId, history = [] }) => {
  const payload = { message };
  if (sessionId) {
    payload.session_id = sessionId;
  } else if (history.length) {
    payload.history = history;
  }
  return payload;
};

export const sendMessage = async ({ message, sessionId, history = [] }) => {
  return requestJson("/chat/", {
    method: "POST",
    body: JSON.stringify(buildPayload({ message, sessionId, history })),
  });
};

export const listSessions = () => requestJson("/chat/sessions");

export const getSessionDetail = (sessionId) => requestJson(`/chat/sessions/${sessionId}`);

export const deleteSession = (sessionId) =>
  requestJson(`/chat/sessions/${sessionId}`, { method: "DELETE" });
