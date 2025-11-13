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
    <div className="card shadow-lg border-0" style={{ height: "75vh", borderRadius: "15px" }}>
      <div 
        className="card-header bg-primary text-white d-flex align-items-center justify-content-between" 
        style={{ borderRadius: "15px 15px 0 0", padding: "1rem" }}
      >
        <div className="d-flex align-items-center">
          <div className="me-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="2"/>
              <path d="M8 10C8 9.44772 8.44772 9 9 9H15C15.5523 9 16 9.44772 16 10V14C16 14.5523 15.5523 15 15 15H9C8.44772 15 8 14.5523 8 14V10Z" fill="white"/>
            </svg>
          </div>
          <div>
            <h5 className="mb-0">Z-GPT Assistant</h5>
            <small className="opacity-75">AI-powered chat, translation & image generation</small>
          </div>
        </div>
        {langNotice && (
          <span className="badge bg-light text-primary">{langNotice}</span>
        )}
      </div>
      
      <div className="card-body overflow-auto p-4" style={{ maxHeight: "calc(75vh - 150px)", backgroundColor: "#f8f9fa" }}>
        {messages.length === 0 && !loading && (
          <div className="text-center text-muted py-5">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" className="mb-3 opacity-50">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
            </svg>
            <p className="mb-2"><strong>Welcome to Z-GPT!</strong></p>
            <p className="small">Start a conversation, generate images, or ask me anything.</p>
            <div className="mt-3 text-start" style={{ maxWidth: "400px", margin: "0 auto" }}>
              <p className="small mb-1"><strong>Try these:</strong></p>
              <ul className="small">
                <li>"What is the capital of France?"</li>
                <li>"Generate an image of a sunset over mountains"</li>
                <li>"پاکستان کا پہلا وزیراعظم کون تھا؟" (Urdu)</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`d-flex mb-3 ${msg.role === "user" ? "justify-content-end" : "justify-content-start"}`}
            style={{ animation: "fadeIn 0.3s ease-in" }}
          >
            {msg.isImage ? (
              <div className="position-relative">
                <img
                  src={msg.content}
                  alt="Generated"
                  className="img-fluid rounded shadow"
                  style={{ maxWidth: "350px", border: "3px solid white" }}
                />
                <div className="position-absolute top-0 end-0 m-2">
                  <span className="badge bg-success">Generated Image</span>
                </div>
              </div>
            ) : (
              <div
                className={`px-4 py-3 rounded-3 shadow-sm ${
                  msg.role === "user"
                    ? "bg-primary text-white"
                    : "bg-white text-dark border"
                }`}
                style={{ 
                  maxWidth: "75%",
                  wordWrap: "break-word",
                  animation: "slideIn 0.3s ease-out"
                }}
              >
                <div className="small opacity-75 mb-1">
                  {msg.role === "user" ? "You" : "Z-GPT"}
                </div>
                <div>{msg.content}</div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="d-flex justify-content-start mb-3">
            <div className="bg-white border px-4 py-3 rounded-3 shadow-sm">
              <div className="d-flex align-items-center">
                <div className="spinner-border spinner-border-sm text-primary me-2" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <span className="text-muted">Z-GPT is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card-footer bg-white border-0 p-3" style={{ borderRadius: "0 0 15px 15px" }}>
        <div className="input-group">
          <input
            type="text"
            className="form-control border-2 py-2"
            placeholder="Type your message... (Shift+Enter for new line)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={loading}
            style={{ borderRadius: "10px 0 0 10px" }}
          />
          <button
            className="btn btn-primary px-4"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{ borderRadius: "0 10px 10px 0" }}
          >
            {loading ? (
              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/>
              </svg>
            )}
          </button>
        </div>
        <div className="small text-muted mt-2 text-center">
          Powered by Mistral-7B & Stable Diffusion • Supports multiple languages
        </div>
      </div>
      
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideIn {
          from { transform: translateY(10px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default ChatBox;
