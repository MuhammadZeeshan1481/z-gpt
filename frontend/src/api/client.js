import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "../auth/tokenStorage";

export const BASE_URL = process.env.REACT_APP_API_BASE || "http://localhost:8000";
export const DEFAULT_HEADERS = { "Content-Type": "application/json" };

export const buildAuthHeaders = () => {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const toError = async (response) => {
  let detail;
  try {
    detail = await response.json();
  } catch (_) {
    detail = {};
  }
  const code = detail?.detail?.code || detail?.error?.code || "request_failed";
  const message =
    detail?.detail?.message || detail?.error?.message || response.statusText || "Request failed";
  const requestId = detail?.detail?.request_id || detail?.request_id;
  const standard = { code, message, status: response.status, requestId };
  const err = new Error(message);
  err.metadata = standard;
  return err;
};

let refreshPromise = null;

export const refreshAuthTokens = async () => {
  if (refreshPromise) {
    return refreshPromise;
  }
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return null;
  }
  refreshPromise = (async () => {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { ...DEFAULT_HEADERS },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) {
      clearTokens();
      throw await toError(res);
    }
    const payload = await res.json();
    setTokens(payload);
    return payload;
  })()
    .catch((error) => {
      clearTokens();
      throw error;
    })
    .finally(() => {
      refreshPromise = null;
    });
  return refreshPromise;
};

export const requestJson = async (path, options = {}) => {
  const { timeout = 30000, headers: customHeaders = {}, ...rest } = options;
  const requestInit = { ...rest };
  const url = `${BASE_URL}${path}`;
  const makeHeaders = () => ({ ...DEFAULT_HEADERS, ...buildAuthHeaders(), ...customHeaders });

  const execute = async () => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      return await fetch(url, {
        ...requestInit,
        headers: makeHeaders(),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timer);
    }
  };

  let response = await execute();
  if (response.status === 401) {
    try {
      const refreshed = await refreshAuthTokens();
      if (refreshed) {
        response = await execute();
      }
    } catch (refreshErr) {
      if (process.env.NODE_ENV !== "test") {
        console.warn("Token refresh failed", refreshErr);
      }
    }
  }

  if (!response.ok) {
    throw await toError(response);
  }
  const text = await response.text();
  if (!text) {
    return null;
  }
  return JSON.parse(text);
};

export const requestBinary = async (path, options = {}) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 60000);
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: { ...buildAuthHeaders(), ...(options.headers || {}) },
      signal: controller.signal,
    });
    if (!res.ok) {
      throw await toError(res);
    }
    return res.arrayBuffer();
  } finally {
    clearTimeout(timeout);
  }
};
