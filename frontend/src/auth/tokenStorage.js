const TOKEN_KEY = "zgpt.auth.tokens";
export const TOKENS_CHANGED_EVENT = "zgpt:tokens_changed";

const safeStorage = () => {
  if (typeof window === "undefined" || !window?.localStorage) {
    return null;
  }
  return window.localStorage;
};

const emitTokenChange = (tokens) => {
  if (typeof window === "undefined" || typeof window.dispatchEvent !== "function") {
    return;
  }
  const event = new CustomEvent(TOKENS_CHANGED_EVENT, { detail: tokens ? { ...tokens } : null });
  window.dispatchEvent(event);
};

let cachedTokens = null;

const readFromStorage = () => {
  if (cachedTokens) {
    return cachedTokens;
  }
  const storage = safeStorage();
  if (!storage) {
    return null;
  }
  try {
    const raw = storage.getItem(TOKEN_KEY);
    cachedTokens = raw ? JSON.parse(raw) : null;
  } catch {
    cachedTokens = null;
  }
  return cachedTokens;
};

const persistTokens = (tokens) => {
  const storage = safeStorage();
  cachedTokens = tokens ? { ...tokens } : null;
  if (!storage) {
    emitTokenChange(cachedTokens);
    return cachedTokens;
  }
  if (!tokens) {
    storage.removeItem(TOKEN_KEY);
    emitTokenChange(cachedTokens);
    return cachedTokens;
  }
  storage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  emitTokenChange(cachedTokens);
  return cachedTokens;
};

export const getTokens = () => readFromStorage();

export const getAccessToken = () => getTokens()?.access_token || null;

export const getRefreshToken = () => getTokens()?.refresh_token || null;

export const setTokens = (tokens) => persistTokens(tokens);

export const clearTokens = () => persistTokens(null);
