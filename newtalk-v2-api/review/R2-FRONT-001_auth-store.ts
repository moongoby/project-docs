import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  roles: string[];
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: AuthUser | null) => void;
  setToken: (token: string | null) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token, isAuthenticated: !!token }),
      clearAuth: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: "newtalk-auth",
      partialize: (s) => ({ token: s.token, user: s.user }),
    }
  )
);
