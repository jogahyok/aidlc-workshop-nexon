"""SSE 이벤트 매니저 — 매장별 단일 스트림"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncGenerator


@dataclass
class SSEEvent:
    event: str
    data: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SSEEventManager:
    """매장(store_id)별 SSE 연결 관리"""

    def __init__(self):
        # store_id → list of asyncio.Queue
        self._connections: dict[int, list[asyncio.Queue]] = {}

    def connect(self, store_id: int) -> asyncio.Queue:
        """새 SSE 연결 등록, Queue 반환"""
        queue: asyncio.Queue = asyncio.Queue()
        if store_id not in self._connections:
            self._connections[store_id] = []
        self._connections[store_id].append(queue)
        return queue

    def disconnect(self, store_id: int, queue: asyncio.Queue):
        """SSE 연결 해제"""
        if store_id in self._connections:
            try:
                self._connections[store_id].remove(queue)
            except ValueError:
                pass
            if not self._connections[store_id]:
                del self._connections[store_id]

    async def broadcast(self, store_id: int, event_type: str, data: dict):
        """매장의 모든 연결에 이벤트 전송"""
        if store_id not in self._connections:
            return

        event = SSEEvent(event=event_type, data=data)
        disconnected = []

        for queue in self._connections[store_id]:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                disconnected.append(queue)

        # 가득 찬 큐 정리
        for queue in disconnected:
            self.disconnect(store_id, queue)

    async def event_generator(
        self, store_id: int, queue: asyncio.Queue
    ) -> AsyncGenerator[str, None]:
        """SSE 이벤트 스트림 생성기"""
        try:
            while True:
                try:
                    event: SSEEvent = await asyncio.wait_for(
                        queue.get(), timeout=30.0
                    )
                    yield self._format_sse(event.event, event.data)
                except asyncio.TimeoutError:
                    # Heartbeat
                    yield self._format_sse(
                        "heartbeat",
                        {"timestamp": datetime.now().isoformat()},
                    )
        except asyncio.CancelledError:
            pass
        finally:
            self.disconnect(store_id, queue)

    def _format_sse(self, event_type: str, data: dict) -> str:
        """SSE 형식으로 포맷팅"""
        json_data = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event_type}\ndata: {json_data}\n\n"

    def get_connection_count(self, store_id: int) -> int:
        """매장의 현재 연결 수"""
        return len(self._connections.get(store_id, []))


# 싱글톤 인스턴스
sse_manager = SSEEventManager()
