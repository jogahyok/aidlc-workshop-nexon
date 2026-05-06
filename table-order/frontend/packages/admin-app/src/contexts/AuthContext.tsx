import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { StorageManager, createApiClient, type AdminAuthState, type AdminLoginResponse } from '@table-order/shared';

interface AdminAuthContextValue extends AdminAuthState {
  login: (storeIdentifier: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AdminAuthContextValue | null>(null);

const TOKEN_KEY = 'admin_auth_token';
const STORE_KEY = 'admin_store_id';

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [authState, setAuthState] = useState<AdminAuthState>({
    isAuthenticated: false,
    token: null,
    storeId: null,
    username: null,
    expiresAt: null,
  });

  const logout = useCallback(() => {
    StorageManager.remove(TOKEN_KEY);
    StorageManager.remove(STORE_KEY);
    setAuthState({ isAuthenticated: false, token: null, storeId: null, username: null, expiresAt: null });
    navigate('/login');
  }, [navigate]);

  const login = useCallback(async (storeIdentifier: string, username: string, password: string) => {
    const apiClient = createApiClient({
      baseUrl: import.meta.env.VITE_API_URL || '/api',
      getToken: () => null,
      onUnauthorized: () => {},
    });

    const response = await apiClient.post<AdminLoginResponse>('/auth/admin/login', {
      storeIdentifier,
      username,
      password,
    });

    const { accessToken, expiresAt, store } = response.data;

    StorageManager.set(TOKEN_KEY, accessToken, 16 * 60 * 60 * 1000); // 16시간
    StorageManager.set(STORE_KEY, store.id);

    setAuthState({
      isAuthenticated: true,
      token: accessToken,
      storeId: store.id,
      username,
      expiresAt,
    });

    navigate('/');
  }, [navigate]);

  // 초기 로드 시 토큰 확인
  useEffect(() => {
    const token = StorageManager.get<string>(TOKEN_KEY);
    const storeId = StorageManager.get<string>(STORE_KEY);

    if (token && storeId) {
      setAuthState({
        isAuthenticated: true,
        token,
        storeId,
        username: null,
        expiresAt: null,
      });
    }
  }, []);

  // 1분마다 만료 체크
  useEffect(() => {
    const interval = setInterval(() => {
      if (StorageManager.isExpired(TOKEN_KEY)) {
        logout();
      }
    }, 60 * 1000);
    return () => clearInterval(interval);
  }, [logout]);

  return (
    <AuthContext.Provider value={{ ...authState, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AdminAuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
