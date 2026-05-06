import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Loading, PageErrorBoundary } from '@table-order/shared';
import { AuthGuard } from './components/AuthGuard';
import { Layout } from './components/Layout';

const MenuPage = lazy(() => import('./pages/MenuPage'));
const MenuDetailPage = lazy(() => import('./pages/MenuDetailPage'));
const CartPage = lazy(() => import('./pages/CartPage'));
const OrderConfirmPage = lazy(() => import('./pages/OrderConfirmPage'));
const OrderHistoryPage = lazy(() => import('./pages/OrderHistoryPage'));
const ErrorPage = lazy(() => import('./pages/ErrorPage'));

export function App() {
  return (
    <Suspense fallback={<Loading fullScreen />}>
      <Routes>
        <Route path="/error" element={<ErrorPage />} />
        <Route element={<AuthGuard />}>
          <Route element={<Layout />}>
            <Route path="/menu" element={
              <PageErrorBoundary pageName="menu"><MenuPage /></PageErrorBoundary>
            } />
            <Route path="/menu/:menuId" element={
              <PageErrorBoundary pageName="menu-detail"><MenuDetailPage /></PageErrorBoundary>
            } />
            <Route path="/cart" element={
              <PageErrorBoundary pageName="cart"><CartPage /></PageErrorBoundary>
            } />
            <Route path="/cart/confirm" element={
              <PageErrorBoundary pageName="order-confirm"><OrderConfirmPage /></PageErrorBoundary>
            } />
            <Route path="/orders" element={
              <PageErrorBoundary pageName="orders"><OrderHistoryPage /></PageErrorBoundary>
            } />
            <Route path="/" element={<Navigate to="/menu" replace />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}
