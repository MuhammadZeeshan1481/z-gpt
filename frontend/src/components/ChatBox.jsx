import React, { useEffect, useRef, useState } from "react";
import { BASE_URL, DEFAULT_HEADERS, buildAuthHeaders, refreshAuthTokens, toError } from "../api/client";
import {
  deleteSession,
  getSessionDetail,
  listSessions,
  sendMessage,
} from "../api/chat";
import { generateImage } from "../api/image";
import StatusBanner from "./ui/StatusBanner";
import { useOnlineStatus } from "../hooks/useOnlineStatus";

const IMAGE_PROMPT_REGEX = /(generate|create|draw)( an)? image/i;
const STREAM_ABORT_CODE = "stream_aborted";
const SESSION_EXPIRED_MESSAGE = "Session expired. Please log in again.";

const ChatBox = ({ forceSync = false }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [langNotice, setLangNotice] = useState("");
  const [error, setError] = useState("");
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [streaming, setStreaming] = useState(false);
  const [sessionQuery, setSessionQuery] = useState("");

  const messagesEndRef = useRef(null);
  const streamControllerRef = useRef(null);
  const online = useOnlineStatus();
  const statusAnnouncement = !online
    ? "Offline. Reconnect to send messages."
    : streaming
    ? "Assistant is streaming a reply."
    : loading
    ? "Assistant is processing a message."
    : "Assistant is idle.";

  const normalizedQuery = sessionQuery.trim().toLowerCase();
  const visibleSessions = normalizedQuery
    ? sessions.filter((session) => {
        const title = session.title || "Untitled chat";
        const preview = session.last_message_preview || "";
        return `${title} ${preview}`.toLowerCase().includes(normalizedQuery);
      })
    : sessions;

  useEffect(() => {
    refreshSessions();
    return () => {
      streamControllerRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    const node = messagesEndRef.current;
    if (node && typeof node.scrollIntoView === "function") {
      node.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const refreshSessions = async () => {
    setSessionsLoading(true);
    setError("");
    try {
      const data = await listSessions();
      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Session list failed", err);
      if (err?.metadata?.status === 401) {
        setError(SESSION_EXPIRED_MESSAGE);
      } else {
        setError("Unable to load previous chats.");
      }
    } finally {
      setSessionsLoading(false);
    }
  };

  const hydrateSession = async (sessionId) => {
    if (!sessionId || sessionId === activeSessionId) {
      return;
    }
    setLoading(true);
    setError("");
    setLangNotice("");
    try {
      const detail = await getSessionDetail(sessionId);
      const hydrated = (detail?.messages || []).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));
      setMessages(hydrated);
      setActiveSessionId(detail?.id || sessionId);
    } catch (err) {
      console.error("Session hydrate failed", err);
      if (err?.metadata?.status === 401) {
        setError(SESSION_EXPIRED_MESSAGE);
      } else {
        setError("Unable to open chat session.");
      }
    } finally {
      setLoading(false);
    }
  };

  const startNewSession = () => {
    if (loading) return;
    if (streaming) {
      streamControllerRef.current?.abort();
    }
    setActiveSessionId(null);
    setMessages([]);
    setLangNotice("");
    setError("");
  };

  const removeAssistantPlaceholder = () => {
    setMessages((prev) => {
      if (!prev.length) return prev;
      return prev.slice(0, -1);
    });
  };

  const updateAssistantMessage = (content) => {
    setMessages((prev) => {
      if (!prev.length) return prev;
      const updated = [...prev];
      const lastIndex = updated.length - 1;
      updated[lastIndex] = { ...updated[lastIndex], content };
      return updated;
    });
  };

  const streamChatResponse = async (text, historyPayload) => {
    const payload = { message: text };
    if (activeSessionId) {
      payload.session_id = activeSessionId;
    } else if (historyPayload.length) {
      payload.history = historyPayload;
    }

    const controller = new AbortController();
    streamControllerRef.current = controller;
    setStreaming(true);
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const executeStream = () =>
        fetch(`${BASE_URL}/chat/stream`, {
          method: "POST",
          headers: { ...DEFAULT_HEADERS, ...buildAuthHeaders() },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

      let res = await executeStream();
      if (res.status === 401) {
        try {
          const refreshed = await refreshAuthTokens();
          if (refreshed) {
            res = await executeStream();
          }
        } catch (refreshErr) {
          console.warn("Silent refresh failed for stream", refreshErr);
        }
      }

      if (!res.ok) {
        throw await toError(res);
      }
      if (!res.body || !res.body.getReader) {
        throw new Error("Streaming not supported in this browser.");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let assistantBuffer = "";

      const processEvent = (block) => {
        const lines = block.split(/\r?\n/);
        let eventType = "message";
        const dataLines = [];
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim();
          } else if (line.startsWith("data:")) {
            dataLines.push(line.replace("data:", "").trim());
          }
        }
        const dataPayload = dataLines.join("\n");
        if (eventType === "message") {
          assistantBuffer += dataPayload;
          updateAssistantMessage(assistantBuffer);
        } else if (eventType === "error") {
          throw new Error(dataPayload || "Stream failed");
        } else if (eventType === "done") {
          let meta = {};
          if (dataPayload) {
            try {
              meta = JSON.parse(dataPayload);
            } catch (err) {
              console.warn("Failed to parse SSE metadata", err);
            }
          }
          if (meta.final_text) {
            assistantBuffer = meta.final_text;
            updateAssistantMessage(assistantBuffer);
          }
          if (meta.detected_lang && meta.detected_lang !== "en") {
            setLangNotice(`📌 Detected language: ${meta.detected_lang.toUpperCase()}`);
          } else {
            setLangNotice("");
          }
          if (meta.session_id) {
            setActiveSessionId(meta.session_id);
          }
        }
      };

      const flushBuffer = (force = false) => {
        let boundary;
        while ((boundary = buffer.indexOf("\n\n")) !== -1) {
          const block = buffer.slice(0, boundary).trim();
          buffer = buffer.slice(boundary + 2);
          if (block) {
            processEvent(block);
          }
        }
        if (force && buffer.trim()) {
          processEvent(buffer.trim());
          buffer = "";
        }
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        flushBuffer();
      }
      flushBuffer(true);
    } catch (err) {
      removeAssistantPlaceholder();
      if (err?.name === "AbortError") {
        const aborted = new Error("Generation cancelled");
        aborted.code = STREAM_ABORT_CODE;
        throw aborted;
      }
      throw err;
    } finally {
      streamControllerRef.current = null;
      setStreaming(false);
    }
  };

  const fetchAssistantReply = async (text, historyPayload) => {
    const res = await sendMessage({ message: text, sessionId: activeSessionId, history: historyPayload });
    const reply = res?.response || "❌ No reply received.";

    if (res?.detected_lang && res.detected_lang !== "en") {
      setLangNotice(`📌 Detected language: ${res.detected_lang.toUpperCase()}`);
    } else {
      setLangNotice("");
    }

    if (res?.session_id) {
      setActiveSessionId(res.session_id);
    }

    setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
  };

  const isImagePrompt = (text) => IMAGE_PROMPT_REGEX.test(text);
  const extractImagePrompt = (text) => text.replace(IMAGE_PROMPT_REGEX, "").replace(/^( of)?/i, "").trim();

  const buildHistoryPayload = (list) =>
    list
      .filter((msg) => !msg.isImage)
      .map(({ role, content }) => ({ role, content }));

  const handleSessionQueryChange = (event) => {
    setSessionQuery(event.target.value);
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading || streaming) return;
    if (!online) {
      setError("You are offline. Reconnect to send messages.");
      return;
    }

    const userMessage = { role: "user", content: trimmed };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    setLangNotice("");
    setError("");

    const historyPayload = activeSessionId ? [] : buildHistoryPayload(nextMessages);
    try {
      if (isImagePrompt(trimmed)) {
        const prompt = extractImagePrompt(trimmed) || trimmed;
        const base64 = await generateImage(prompt);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", isImage: true, content: `data:image/png;base64,${base64}` },
        ]);
        await refreshSessions();
      } else {
        const shouldStream = !forceSync;
        if (shouldStream) {
          try {
            await streamChatResponse(trimmed, historyPayload);
          } catch (streamErr) {
            if (streamErr?.code === STREAM_ABORT_CODE) {
              throw streamErr;
            }
            console.warn("Streaming unavailable, falling back", streamErr);
            await fetchAssistantReply(trimmed, historyPayload);
          }
        } else {
          await fetchAssistantReply(trimmed, historyPayload);
        }
        await refreshSessions();
      }
    } catch (err) {
      console.error("Send failed", err);
      if (err?.metadata?.status === 401) {
        setError(SESSION_EXPIRED_MESSAGE);
      } else {
        const friendly = err?.code === STREAM_ABORT_CODE ? err.message : err?.message || "Failed to process message.";
        setError(friendly);
        if (err?.code !== STREAM_ABORT_CODE) {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "⚠️ Error: failed to process message." },
          ]);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const cancelStreaming = () => {
    streamControllerRef.current?.abort();
  };

  const handleDeleteSession = async (sessionId, event) => {
    event.stopPropagation();
    try {
      await deleteSession(sessionId);
      if (sessionId === activeSessionId) {
        startNewSession();
      }
      await refreshSessions();
    } catch (err) {
      console.error("Delete failed", err);
      if (err?.metadata?.status === 401) {
        setError(SESSION_EXPIRED_MESSAGE);
      } else {
        setError("Unable to delete chat session.");
      }
    }
  };

  return (
    <div className="row g-3">
      <div className="col-12 col-lg-4">
        <div className="card h-100 shadow-sm">
          <div className="card-header d-flex justify-content-between align-items-center">
            <div>
              <h6 className="mb-0">Conversations</h6>
              <small className="text-muted">Stored locally in SQLite</small>
            </div>
            <div className="btn-group">
              <button
                className="btn btn-sm btn-outline-secondary"
                onClick={refreshSessions}
                disabled={sessionsLoading}
              >
                {sessionsLoading ? "Loading" : "Refresh"}
              </button>
              <button
                className="btn btn-sm btn-primary"
                onClick={startNewSession}
                disabled={loading || streaming}
              >
                New Chat
              </button>
            </div>
          </div>
          <div className="px-3 py-2 border-bottom">
            <input
              type="search"
              className="form-control form-control-sm"
              placeholder="Search conversations"
              value={sessionQuery}
              onChange={handleSessionQueryChange}
              aria-label="Search chat sessions"
            />
          </div>
          <div className="list-group list-group-flush overflow-auto" style={{ maxHeight: "60vh" }}>
            {sessionsLoading && (
              <div className="list-group-item text-center text-muted">Loading sessions...</div>
            )}
            {!sessionsLoading && sessions.length === 0 && (
              <div className="list-group-item text-center text-muted">No conversations yet</div>
            )}
            {!sessionsLoading && sessions.length > 0 && visibleSessions.length === 0 && (
              <div className="list-group-item text-center text-muted">No matches for your search</div>
            )}
            {visibleSessions.map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <div
                  key={session.id}
                  role="button"
                  tabIndex={0}
                  className={`list-group-item list-group-item-action d-flex justify-content-between align-items-start ${
                    isActive ? "active" : ""
                  }`}
                  onClick={() => hydrateSession(session.id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      hydrateSession(session.id);
                    }
                  }}
                >
                  <div className="me-2">
                    <div className="fw-semibold text-truncate" style={{ maxWidth: "12rem" }}>
                      {session.title || "Untitled chat"}
                    </div>
                    <small className="text-muted">
                      {session.last_message_preview || "No messages yet"}
                    </small>
                  </div>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-danger"
                    onClick={(e) => handleDeleteSession(session.id, e)}
                  >
                    ×
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="col-12 col-lg-8">
        <div className="card shadow p-3" style={{ height: "70vh" }}>
          <StatusBanner online={online} streaming={streaming} loading={loading} />
          <div className="card-body overflow-auto" style={{ maxHeight: "calc(70vh - 110px)" }}>
            <span className="visually-hidden" aria-live="polite">
              {statusAnnouncement}
            </span>
            {langNotice && (
              <div className="text-muted small mb-2 text-center">{langNotice}</div>
            )}

            {error && (
              <div className="alert alert-warning py-2 d-flex justify-content-between align-items-center gap-2">
                <span>{error}</span>
                <div className="btn-group btn-group-sm">
                  <button type="button" className="btn btn-outline-secondary" onClick={() => setError("")}>
                    Dismiss
                  </button>
                  <button type="button" className="btn btn-outline-primary" onClick={refreshSessions}>
                    Retry
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={`msg-${idx}`}
                className={`d-flex my-2 ${msg.role === "user" ? "justify-content-end" : "justify-content-start"}`}
              >
                {msg.isImage ? (
                  <img
                    src={msg.content}
                    alt="Generated"
                    className="img-fluid rounded shadow-sm"
                    style={{ maxWidth: "300px" }}
                  />
                ) : (
                  <div
                    className={`px-3 py-2 rounded ${
                      msg.role === "user" ? "bg-primary text-white" : "bg-light text-dark"
                    }`}
                    style={{ maxWidth: "75%" }}
                  >
                    {msg.content}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />

            {(loading || streaming) && (
              <div className="text-start">
                <span className="badge bg-secondary">{streaming ? "Streaming..." : "Typing..."}</span>
              </div>
            )}
          </div>

          <div className="input-group mt-3">
            <input
              type="text"
              className="form-control"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              disabled={loading || streaming}
            />
            <button className="btn btn-primary" onClick={handleSend} disabled={loading || streaming}>
              Send
            </button>
            {streaming && (
              <button
                type="button"
                className="btn btn-outline-danger"
                onClick={cancelStreaming}
                disabled={!streaming}
              >
                Stop
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
