import React, { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

type User = {
  id: string;
  name: string;
  email: string;
  role: "ADMIN" | "GESTOR" | "OPERADOR" | "VISUALIZADOR";
  company_id: string;
};

type AuthContextData = {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadSession() {
    try {
      const response = await api.get("/users/me");
      setUser(response.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const response = await api.post("/auth/login", { email, password });

    const { access_token } = response.data;

    // Mobile: Store token in local storage
    api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

    await loadSession();
  }

  function logout() {
    localStorage.removeItem("token");
    setUser(null);
  }

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      loadSession();
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuthContext() {
  return useContext(AuthContext);
}