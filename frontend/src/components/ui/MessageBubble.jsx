import React from "react";

const MessageBubble = ({ role, content, isImage }) => {
  const isUser = role === "user";
  return (
    <div className={`w-full flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-xl px-4 py-2 shadow ${
          isUser ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"
        }`}
      >
        {isImage ? (
          <img
            src={content}
            alt="Generated"
            className="rounded-lg max-w-xs border"
          />
        ) : (
          <p className="whitespace-pre-line">{content}</p>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
