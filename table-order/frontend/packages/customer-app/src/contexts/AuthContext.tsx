import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { StorageManager, createApiClient, type AuthState, type AuthMeResponse } from '@table-order/shared';

interface AuthContextValue extends AuthState {
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = 'customer_auth_token';
const EXPIRES_KEY = 'customer_auth_expires';

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    token: null,
    userType: null,
    storeId: null,
    tableId: null,
    tableNumber: null,
    expiresAt: null,
  });
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    StorageManager.remove(TOKEN_KEY);
    StorageManager.remove(EXPIRES_KEY);
    setAuthState({
      isAuthenticated: false,
      token: null,
      userType: null,
      storeId: null,
      tableId: null,
      tableNumber: null,
      expiresAt: null,
    });
    navigate('/error');
  }, [navigate]);

  useEffect(() => {
    const initAuth = async () => {
      const token = StorageManager.get<string>(TOKEN_KEY);
      const expiresAt = StorageManager.get<string>(EXPIRES_KEY);

      if (!token || !expiresAt) {
        setIsLoading(false);
        navigate('/error');
        return;
      }

      if (new Date(expiresAt).getTime() < Date.now()) {
        logout();
        setIsLoading(false);
        return;
      }

      try {
        const apiClient = createApiClient({
          baseUrl: import.meta.env.VITE_API_URL || '/api',
          getToken: () => token,
          onUnauthorized: logout,
        });

        const response = await apiClient.get<AuthMeResponse>('/auth/me');
        const data = response.data;

        setAuthState({
          isAuthenticated: true,
          token,
          userType: data.userType,
          storeId: data.storeId,
          tableId: data.tableId ?? null,
          tableNumber: data.tableNumber ?? null,
          expiresAt,
        });
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (isLoading) {
    return null; // AuthGuard에서 Loading 표시
  }

  return (
    <AuthContext.Provider value={{ ...authState, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
