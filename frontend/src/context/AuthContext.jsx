import { createContext, useCallback, useContext, useEffect, useState } from "react";

import * as authApi from "../api/auth";
import { setUnauthorizedHandler, tokenStore } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Only show the "checking" screen when there is a saved token to verify.
  const [checking, setChecking] = useState(() => Boolean(tokenStore.get()));
  const [notice, setNotice] = useState("");

  const logout = useCallback((message = "") => {
    tokenStore.clear();
    setUser(null);
    setNotice(message);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => logout("Your session has expired. Please log in again."));
  }, [logout]);

  // On page load, turn a saved token back into a user (or drop it if it expired).
  useEffect(() => {
    if (!tokenStore.get()) return;
    authApi
      .getMe()
      .then(setUser)
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);

  async function login(email, password) {
    const { access_token } = await authApi.login(email, password);
    tokenStore.set(access_token);
    const me = await authApi.getMe();
    setNotice("");
    setUser(me);
  }

  async function register(email, password) {
    await authApi.register(email, password);
    await login(email, password);
  }

  return (
    <AuthContext.Provider value={{ user, checking, notice, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
