import { useEffect, useState } from "react";

export const useOnlineStatus = () => {
  const getStatus = () => (typeof navigator !== "undefined" ? navigator.onLine : true);
  const [online, setOnline] = useState(getStatus);

  useEffect(() => {
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return online;
};
