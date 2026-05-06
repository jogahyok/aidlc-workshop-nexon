import { useState, useCallback, type ReactNode } from 'react';
import { Snackbar, Alert, Button } from '@mui/material';
import { ToastContext, type ToastItem, type ToastOptions } from '../../hooks/useToast';

const MAX_TOASTS = 3;
const DEFAULT_DURATIONS: Record<string, number> = {
  success: 3000,
  info: 3000,
  warning: 4000,
  error: 5000,
};

interface ToastProviderProps {
  children: ReactNode;
  position?: 'bottom-center' | 'top-right';
}

export function ToastProvider({ children, position = 'bottom-center' }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const showToast = useCallback((options: ToastOptions) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const newToast: ToastItem = { ...options, id };

    setToasts((prev) => {
      const updated = [...prev, newToast];
      return updated.slice(-MAX_TOASTS);
    });

    const duration = options.duration ?? DEFAULT_DURATIONS[options.severity] ?? 3000;
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const closeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const anchorOrigin =
    position === 'top-right'
      ? { vertical: 'top' as const, horizontal: 'right' as const }
      : { vertical: 'bottom' as const, horizontal: 'center' as const };

  return (
    <ToastContext.Provider value={{ toasts, showToast, closeToast }}>
      {children}
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open
          anchorOrigin={anchorOrigin}
          data-testid={`toast-${toast.severity}`}
        >
          <Alert
            severity={toast.severity}
            onClose={() => closeToast(toast.id)}
            action={
              toast.action ? (
                <Button color="inherit" size="small" onClick={toast.action.onClick}>
                  {toast.action.label}
                </Button>
              ) : undefined
            }
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </ToastContext.Provider>
  );
}
