import { Navigate, Outlet } from 'react-router-dom';
import { Loading } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';

export function AuthGuard() {
  const { isAuthenticated, token } = useAuth();

  if (token === null && !isAuthenticated) {
    return <Loading fullScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/error" replace />;
  }

  return <Outlet />;
}
