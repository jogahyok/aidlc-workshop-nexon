import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Loading, PageErrorBoundary } from '@table-order/shared';
import { AuthGuard } from './components/AuthGuard';
import { AppLayout } from './components/AppLayout';

const LoginPage = lazy(() => import('./pages/LoginPage'));
const OrderDashboard = lazy(() => import('./pages/OrderDashboard'));
const TableManagementPage = lazy(() => import('./pages/TableManagementPage'));
const MenuManagementPage = lazy(() => import('./pages/MenuManagementPage'));
const MenuFormPage = lazy(() => import('./pages/MenuFormPage'));

export function App() {
  return (
    <Suspense fallback={<Loading fullScreen />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AuthGuard />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={
              <PageErrorBoundary pageName="dashboard"><OrderDashboard /></PageErrorBoundary>
            } />
            <Route path="/tables" element={
              <PageErrorBoundary pageName="tables"><TableManagementPage /></PageErrorBoundary>
            } />
            <Route path="/menus" element={
              <PageErrorBoundary pageName="menus"><MenuManagementPage /></PageErrorBoundary>
            } />
            <Route path="/menus/new" element={
              <PageErrorBoundary pageName="menu-form"><MenuFormPage /></PageErrorBoundary>
            } />
            <Route path="/menus/:menuId/edit" element={
              <PageErrorBoundary pageName="menu-form"><MenuFormPage /></PageErrorBoundary>
            } />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
