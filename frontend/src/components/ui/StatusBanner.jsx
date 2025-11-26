import React from "react";

const StatusBanner = ({ online, streaming, loading }) => {
  let variant = null;
  let message = "";

  if (!online) {
    variant = "warning";
    message = "You are offline. Reconnect to send or receive messages.";
  } else if (streaming) {
    variant = "info";
    message = "Streaming response in real time...";
  } else if (loading) {
    variant = "secondary";
    message = "Processing your request...";
  }

  if (!variant) {
    return null;
  }

  return (
    <div className={`alert alert-${variant} py-2 mb-3`} role="status" aria-live="polite">
      {message}
    </div>
  );
};

export default StatusBanner;
