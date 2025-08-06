import React, { useState } from "react";
import { sendMessage } from "../api/chat";
import { generateImage } from "../api/image";

const ChatBox = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [langNotice, setLangNotice] = useState("");

  const isImagePrompt = (text) => /(generate|create|draw)( an)? image/i.test(text);
  const extractImagePrompt = (text) =>
    text.replace(/^(generate|create|draw)( an)? image( of)?/i, "").trim();

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);
    setLangNotice("");

    try {
      if (isImagePrompt(input)) {
        const prompt = extractImagePrompt(input) || input;
        const base64 = await generateImage(prompt);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", isImage: true, content: `data:image/png;base64,${base64}` },
        ]);
      } else {
        const res = await sendMessage(input, updatedMessages);
        const reply = res?.response || "❌ No reply received.";

        if (res?.detected_lang && res.detected_lang !== "en") {
          setLangNotice(`📌 Detected language: ${res.detected_lang.toUpperCase()}`);
        }

        setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      }
    } catch (err) {
      console.error("Send failed:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Error: failed to process message." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card shadow p-3" style={{ height: "70vh" }}>
      <div className="card-body overflow-auto" style={{ maxHeight: "calc(70vh - 100px)" }}>
        {langNotice && (
          <div className="text-muted small mb-2 text-center">{langNotice}</div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
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
                  msg.role === "user"
                    ? "bg-primary text-white"
                    : "bg-light text-dark"
                }`}
                style={{ maxWidth: "75%" }}
              >
                {msg.content}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="text-start">
            <span className="badge bg-secondary">Typing...</span>
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
        />
        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
