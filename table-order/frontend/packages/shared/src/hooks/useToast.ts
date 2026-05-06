import { createContext, useContext, useCallback, useRef } from 'react';

export type ToastSeverity = 'success' | 'error' | 'warning' | 'info';

export interface ToastOptions {
  message: string;
  severity: ToastSeverity;
  duration?: number;
  action?: { label: string; onClick: () => void };
}

export interface ToastItem extends ToastOptions {
  id: string;
}

export interface ToastContextValue {
  toasts: ToastItem[];
  showToast: (options: ToastOptions) => void;
  closeToast: (id: string) => void;
}

export const ToastContext = createContext<ToastContextValue | null>(null);

/**
 * Toast 알림을 표시하는 훅입니다.
 */
export function useToast(): Pick<ToastContextValue, 'showToast' | 'closeToast'> {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return { showToast: context.showToast, closeToast: context.closeToast };
}

/**
 * 중복 방지를 위한 최근 메시지 추적 훅입니다.
 */
export function useDeduplicatedToast() {
  const lastMessage = useRef<string>('');
  const lastTime = useRef<number>(0);
  const { showToast, closeToast } = useToast();

  const showDeduplicatedToast = useCallback(
    (options: ToastOptions) => {
      const now = Date.now();
      if (options.message === lastMessage.current && now - lastTime.current < 2000) {
        return; // 2초 이내 동일 메시지 무시
      }
      lastMessage.current = options.message;
      lastTime.current = now;
      showToast(options);
    },
    [showToast],
  );

  return { showToast: showDeduplicatedToast, closeToast };
}
