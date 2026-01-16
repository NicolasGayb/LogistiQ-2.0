import { createContext, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiFetch } from '../api/client';
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
      const response = await apiFetch('/auth/me');
      const data: UserMe = await response.json();
      setUser(data);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);

    const response = await fetch(
      `${process.env.EXPO_PUBLIC_API_URL}/auth/login`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: body.toString(),
      }
    );

    const data: LoginResponse = await response.json();

    await AsyncStorage.setItem('access_token', data.access_token);
    await loadUser();
  }

  async function logout() {
    await AsyncStorage.removeItem('access_token');
    setUser(null);
  }

  useEffect(() => {
    AsyncStorage.getItem('access_token').then((token) => {
      if (token) {
        loadUser();
      } else {
        setLoading(false);
      }
    });
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