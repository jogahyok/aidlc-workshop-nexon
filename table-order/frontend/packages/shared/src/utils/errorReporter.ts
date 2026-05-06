export interface ErrorReport {
  timestamp: string;
  errorType: 'runtime' | 'network' | 'validation' | 'unhandled';
  message: string;
  stack?: string;
  componentStack?: string;
  url: string;
  userAgent: string;
  context?: Record<string, unknown>;
}

const ERROR_ENDPOINT = '/api/errors';
const BATCH_SIZE = 5;
const FLUSH_INTERVAL = 10000;

let errorQueue: ErrorReport[] = [];
let flushTimer: ReturnType<typeof setTimeout> | null = null;

function filterSensitiveData(data: Record<string, unknown>): Record<string, unknown> {
  const sensitiveKeys = ['token', 'password', 'authorization', 'secret', 'credential'];
  const filtered: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(data)) {
    if (sensitiveKeys.some((sk) => key.toLowerCase().includes(sk))) {
      filtered[key] = '[REDACTED]';
    } else {
      filtered[key] = value;
    }
  }

  return filtered;
}

function flushErrors(): void {
  if (errorQueue.length === 0) return;

  const batch = [...errorQueue];
  errorQueue = [];

  // 비동기 전송 — 실패해도 앱에 영향 없음
  fetch(ERROR_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(batch),
  }).catch(() => {
    // 전송 실패 무시
  });
}

function scheduleFlush(): void {
  if (flushTimer) return;
  flushTimer = setTimeout(() => {
    flushTimer = null;
    flushErrors();
  }, FLUSH_INTERVAL);
}

/**
 * 에러를 큐에 추가합니다. 배치 크기 도달 시 즉시 전송합니다.
 */
export function reportError(report: Omit<ErrorReport, 'timestamp' | 'url' | 'userAgent'>): void {
  const fullReport: ErrorReport = {
    ...report,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    context: report.context ? filterSensitiveData(report.context) : undefined,
  };

  errorQueue.push(fullReport);

  if (errorQueue.length >= BATCH_SIZE) {
    flushErrors();
  } else {
    scheduleFlush();
  }
}

/**
 * 글로벌 에러 핸들러를 등록합니다.
 */
export function setupGlobalErrorHandler(): void {
  window.addEventListener('error', (event) => {
    reportError({
      errorType: 'unhandled',
      message: event.message,
      stack: event.error?.stack,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    reportError({
      errorType: 'unhandled',
      message: event.reason?.message || 'Unhandled Promise Rejection',
      stack: event.reason?.stack,
    });
  });
}
