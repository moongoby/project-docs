import Cookies from "js-cookie";
import { useAuthStore } from "@/stores/auth-store";
import type { ApiResponse, LoginResponse, User } from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://114.207.244.86:8080/api";
const TOKEN_KEY = "newtalk_token";

export function getToken(): string | undefined {
  if (typeof window === "undefined") return undefined;
  return useAuthStore.getState().token ?? Cookies.get(TOKEN_KEY);
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL.replace(/\/$/, "")}/${endpoint.replace(/^\//, "")}`;
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.message || data?.error || `HTTP ${res.status}`);
  }
  return data as ApiResponse<T>;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.message || data?.error || "로그인 실패");
  }
  const token = data?.token ?? data?.data?.token;
  const user = data?.user ?? data?.data?.user;
  if (token) {
    Cookies.set(TOKEN_KEY, token, { expires: 7, sameSite: "lax" });
    useAuthStore.getState().setToken(token);
  }
  if (user) {
    useAuthStore.getState().setUser(user);
  }
  return { token, user } as LoginResponse;
}

export async function logout(): Promise<void> {
  const token = getToken();
  try {
    await fetch(`${BASE_URL}/auth/logout`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  } finally {
    Cookies.remove(TOKEN_KEY);
    useAuthStore.getState().clearAuth();
  }
}

export async function getMe(): Promise<User> {
  const res = await fetchApi<User>("auth/me");
  if (res.data) useAuthStore.getState().setUser(res.data);
  return res.data;
}
