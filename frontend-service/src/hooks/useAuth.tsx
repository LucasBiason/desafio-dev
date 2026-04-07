import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import type { User, AuthContextType } from '../types/auth';

const AuthContext = createContext<AuthContextType | null>(null);

function loadStoredUser(): User | null {
  const storedUser = localStorage.getItem('user');
  const storedToken = localStorage.getItem('access_token');
  if (storedUser && storedToken) {
    try {
      return JSON.parse(storedUser) as User;
    } catch {
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
    }
  }
  return null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser);

  const login = async (credentials: { username: string; password: string }) => {
    const data = await authService.login(credentials);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    window.location.href = `${import.meta.env.BASE_URL}login`;
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, loading: false }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
