import type { Store, Table, TableSession } from './store';

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  userType: 'admin' | 'table' | null;
  storeId: string | null;
  tableId?: string | null;
  tableNumber?: number | null;
  expiresAt: string | null;
}

export interface AdminAuthState {
  isAuthenticated: boolean;
  token: string | null;
  storeId: string | null;
  username: string | null;
  expiresAt: string | null;
}

export interface AdminLoginRequest {
  storeIdentifier: string;
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  accessToken: string;
  expiresAt: string;
  store: Store;
  username: string;
}

export interface TableLoginResponse {
  accessToken: string;
  expiresAt: string;
  store: Store;
  table: Table;
  session: TableSession;
}

export interface AuthMeResponse {
  userType: 'admin' | 'table';
  storeId: string;
  tableId?: string;
  tableNumber?: number;
  username?: string;
}
