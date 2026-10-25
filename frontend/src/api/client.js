// One place for talking to the FastAPI backend: base URL, JSON, the auth
// header and turning error responses into readable messages.

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "autodeal_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

// AuthContext registers a handler so any 401 logs the user out.
let onUnauthorized = () => {};
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

// FastAPI returns `detail` as a string, or as a list of field errors for 422s.
function describeError(status, body) {
  const detail = body?.detail;
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const field = err.loc?.filter((part) => part !== "body").join(".");
        const message = err.msg.replace(/^Value error, /, "");
        return field ? `${field}: ${message}` : message;
      })
      .join("; ");
  }
  if (typeof detail === "string") return detail;
  if (status === 403) return "Admin access required";
  return `Request failed (${status})`;
}

export async function request(path, { method = "GET", body, params } = {}) {
  const url = new URL(path, API_URL);
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== "" && value != null) url.searchParams.set(key, value);
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(url, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Cannot reach the server. Is the backend running?");
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // A 401 on login just means wrong credentials, not an expired session.
    if (response.status === 401 && token) onUnauthorized();
    throw new ApiError(response.status, describeError(response.status, data));
  }
  return data;
}
