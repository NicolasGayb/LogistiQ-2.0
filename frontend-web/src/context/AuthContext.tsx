import { createContext, useContext, useEffect, useState } from 'react';
import api from '../api/client';
import { UserMe, LoginResponse } from '../types/auth';

interface AuthContextData {
  user: UserMe | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user;

  async function loadUser() {
    try {
      const response = await api.get<UserMe>('/auth/me');
      setUser(response.data);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await api.post<LoginResponse>(
      '/auth/login',
      params
    );

    localStorage.setItem('access_token', response.data.access_token);
    await loadUser();
  }

  function logout() {
    localStorage.removeItem('access_token');
    setUser(null);
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, loading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}