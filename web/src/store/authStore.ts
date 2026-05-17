import { create } from 'zustand';
import { api, tokenStore } from '@/api/client';

export interface User {
  id: string;
  email: string;
  display_name: string;
  avatar_url?: string;
  plan?: 'free' | 'pro' | 'enterprise';
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setIsAuthenticated: (value: boolean) => void;
  setIsLoading: (value: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  updateUser: (patch: Partial<User>) => void;
  logout: () => void;
  loginWithToken: (token: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setIsAuthenticated: (value) => set({ isAuthenticated: value }),
  setIsLoading: (value) => set({ isLoading: value }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  updateUser: (patch) => {
    const current = get().user;
    if (current) set({ user: { ...current, ...patch } });
  },
  logout: () => {
    tokenStore.clear();
    localStorage.removeItem('token');
    localStorage.removeItem('pv_ext_token');
    window.dispatchEvent(new Event('PV_AUTH_LOGOUT'));
    set({ user: null, isAuthenticated: false, error: null });
  },
  loginWithToken: async (token: string) => {
    set({ isLoading: true });
    try {
      localStorage.setItem('token', token);
      localStorage.setItem('pv_ext_token', token);
      tokenStore.set(token);
      window.dispatchEvent(new CustomEvent('PV_AUTH_SYNC', { detail: { token } }));
      const user = await api.get<User>('/auth/me');
      set({ user, isAuthenticated: true, error: null, isLoading: false });
    } catch (err) {
      tokenStore.clear();
      localStorage.removeItem('token');
      localStorage.removeItem('pv_ext_token');
      set({ isAuthenticated: false, user: null, error: 'Failed to sign in with Google', isLoading: false });
      throw err;
    }
  },
  refreshUser: async () => {
    set({ isLoading: true });
    try {
      let token = tokenStore.get();
      if (!token) {
        token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
        if (token) tokenStore.set(token);
      }

      if (!token) {
        set({ isLoading: false });
        return;
      }

      const user = await api.get<User>('/auth/me');
      set({ user, isAuthenticated: true, error: null, isLoading: false });
    } catch {
      tokenStore.clear();
      localStorage.removeItem('token');
      set({ isAuthenticated: false, user: null, isLoading: false });
    }
  },
}));
