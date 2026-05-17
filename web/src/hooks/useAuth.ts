import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore, type User } from "@/store/authStore";
import { api, tokenStore } from "@/api/client";

interface AuthResponse {
  access_token: string;
  user: User;
}

export function useAuth() {
  const navigate = useNavigate();
  const { setUser, setError, error, clearError } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    clearError();
    setIsLoading(true);
    try {
      const { access_token, user } = await api.post<AuthResponse>("/auth/login", { email, password });
      localStorage.setItem("token", access_token);
      tokenStore.set(access_token);
      setUser(user);
      navigate("/");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const message = axiosErr.response?.data?.detail ?? axiosErr.message ?? "Login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [navigate, setUser, setError, clearError]);

  const register = useCallback(async (email: string, password: string, displayName: string) => {
    clearError();
    setIsLoading(true);
    try {
      const { access_token, user } = await api.post<AuthResponse>("/auth/register", { email, password, display_name: displayName });
      localStorage.setItem("token", access_token);
      tokenStore.set(access_token);
      setUser(user);
      navigate("/");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const message = axiosErr.response?.data?.detail ?? axiosErr.message ?? "Registration failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [navigate, setUser, setError, clearError]);

  const loginWithGoogle = useCallback(async (code: string) => {
    setIsLoading(true);
    try {
      const { access_token, user } = await api.post<AuthResponse>("/auth/google-callback", { code });
      localStorage.setItem("token", access_token);
      tokenStore.set(access_token);
      setUser(user);
      navigate("/");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const message = axiosErr.response?.data?.detail ?? axiosErr.message ?? "Google login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [navigate, setUser, setError, clearError]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login");
  }, [navigate, setUser]);

  return {
    login,
    register,
    loginWithGoogle,
    logout,
    isLoading,
    error,
    clearError,
  };
}
