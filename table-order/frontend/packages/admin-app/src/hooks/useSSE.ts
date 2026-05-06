import { useEffect, useRef, useState, useCallback } from 'react';
import type { OrderEvent } from '@table-order/shared';

type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'failed';

interface UseSSEConfig {
  url: string;
  token: string;
  onEvent: (event: OrderEvent) => void;
  enabled?: boolean;
  maxReconnects?: number;
  reconnectInterval?: number;
}

export function useSSE({
  url,
  token,
  onEvent,
  enabled = true,
  maxReconnects = 5,
  reconnectInterval = 3000,
}: UseSSEConfig) {
  const [connectionState, setConnectionState] = useState<SSEConnectionState>('disconnected');
  const reconnectCount = useRef(0);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    setConnectionState('connecting');

    // SSE는 Authorization 헤더를 지원하지 않으므로 URL 파라미터로 토큰 전달
    const sseUrl = `${url}?token=${encodeURIComponent(token)}`;
    const eventSource = new EventSource(sseUrl);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnectionState('connected');
      reconnectCount.current = 0;
    };

    eventSource.onmessage = (event) => {
      try {
        const data: OrderEvent = JSON.parse(event.data);
        onEvent(data);
      } catch {
        // 파싱 실패 무시
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      eventSourceRef.current = null;

      if (reconnectCount.current < maxReconnects) {
        setConnectionState('disconnected');
        reconnectCount.current++;
        setTimeout(connect, reconnectInterval);
      } else {
        setConnectionState('failed');
      }
    };
  }, [url, token, onEvent, enabled, maxReconnects, reconnectInterval]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setConnectionState('disconnected');
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectCount.current = 0;
    connect();
  }, [connect, disconnect]);

  useEffect(() => {
    if (enabled) connect();
    return () => disconnect();
  }, [enabled, connect, disconnect]);

  return { connectionState, reconnect, disconnect };
}
