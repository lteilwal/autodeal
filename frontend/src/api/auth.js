import { request } from "./client";

export const register = (email, password) =>
  request("/api/auth/register", { method: "POST", body: { email, password } });

export const login = (email, password) =>
  request("/api/auth/login", { method: "POST", body: { email, password } });

export const getMe = () => request("/api/auth/me");
