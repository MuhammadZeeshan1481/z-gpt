import React from "react";

const TypingIndicator = () => (
  <div className="flex gap-1 items-center px-3 py-1">
    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
  </div>
);

export default TypingIndicator;
