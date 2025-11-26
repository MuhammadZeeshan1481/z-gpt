import { requestJson } from "./client";

export const signup = (payload) =>
  requestJson("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const login = (payload) =>
  requestJson("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const refresh = (payload) =>
  requestJson("/auth/refresh", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getProfile = () => requestJson("/auth/me");
