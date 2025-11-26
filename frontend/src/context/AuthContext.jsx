import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { login as loginRequest, signup as signupRequest, refresh as refreshRequest, getProfile } from "../api/auth";
import {
  TOKENS_CHANGED_EVENT,
  clearTokens,
  getRefreshToken,
  getTokens as readTokens,
  setTokens as persistTokens,
} from "../auth/tokenStorage";

export const AuthContext = createContext(undefined);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(() => readTokens());
  const [initializing, setInitializing] = useState(true);

  const syncTokens = useCallback((nextTokens) => {
    persistTokens(nextTokens);
    setTokens(nextTokens ? { ...nextTokens } : null);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    const handleTokenChange = (event) => {
      const next = event.detail || null;
      setTokens((prev) => {
        const hasSameAccess = prev?.access_token === next?.access_token;
        const hasSameRefresh = prev?.refresh_token === next?.refresh_token;
        if ((!prev && !next) || (hasSameAccess && hasSameRefresh)) {
          return prev;
        }
        return next ? { ...next } : null;
      });
      if (!next) {
        setUser(null);
      }
    };
    window.addEventListener(TOKENS_CHANGED_EVENT, handleTokenChange);
    return () => window.removeEventListener(TOKENS_CHANGED_EVENT, handleTokenChange);
  }, []);

  useEffect(() => {
    let active = true;
    const bootstrap = async () => {
      if (!tokens?.access_token) {
        setInitializing(false);
        return;
      }
      try {
        const profile = await getProfile();
        if (active) {
          setUser(profile);
        }
      } catch {
        syncTokens(null);
        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setInitializing(false);
        }
      }
    };
    bootstrap();
    return () => {
      active = false;
    };
  }, [tokens, syncTokens]);

  const hydrateUser = useCallback(async () => {
    const profile = await getProfile();
    setUser(profile);
    return profile;
  }, []);

  const handleAuthResult = useCallback(
    async (tokenResponse) => {
      setInitializing(true);
      try {
        syncTokens(tokenResponse);
        await hydrateUser();
      } finally {
        setInitializing(false);
      }
    },
    [hydrateUser, syncTokens]
  );

  const login = useCallback(
    async (payload) => {
      const response = await loginRequest(payload);
      await handleAuthResult(response);
    },
    [handleAuthResult]
  );

  const signup = useCallback(
    async (payload) => {
      const response = await signupRequest(payload);
      await handleAuthResult(response);
    },
    [handleAuthResult]
  );

  const logout = useCallback(() => {
    clearTokens();
    syncTokens(null);
    setUser(null);
    setInitializing(false);
  }, [syncTokens]);

  const refreshTokens = useCallback(async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }
    const response = await refreshRequest({ refresh_token: refreshToken });
    syncTokens(response);
    return response;
  }, [syncTokens]);

  const value = useMemo(
    () => ({
      user,
      tokens,
      isAuthenticated: Boolean(user),
      loading: initializing,
      login,
      signup,
      logout,
      refreshTokens,
    }),
    [user, tokens, initializing, login, signup, logout, refreshTokens]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
