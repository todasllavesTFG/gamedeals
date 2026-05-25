import { createContext, useContext, useEffect, useState } from 'react';
import * as api from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(api.getToken);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = api.getToken();
    if (!stored) {
      setLoading(false);
      return;
    }
    api.getMe()
      .then(setUser)
      .catch(() => api.clearToken())
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const handler = () => logout();
    window.addEventListener('auth:unauthorized', handler);
    return () => window.removeEventListener('auth:unauthorized', handler);
  }, []);

  async function login(email, password) {
    const data = await api.login({ email, password });
    api.setToken(data.access_token);
    setTokenState(data.access_token);
    const me = await api.getMe();
    setUser(me);
  }

  async function register(email, username, password) {
    await api.register({ email, username, password });
    await login(email, password);
  }

  function logout() {
    api.clearToken();
    setTokenState(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, register, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
