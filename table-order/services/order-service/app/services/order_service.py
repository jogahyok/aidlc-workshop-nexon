"""주문 비즈니스 로직"""

import json
import math
from typing import Optional

from app.db.connection import get_pool
from app.db.mappers.mappers import (
    map_order,
    map_order_item,
    map_order_item_option,
    map_order_history,
)
from app.db.queries import order_queries as q
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_option import OrderItemOption
from app.models.order_history import OrderHistory
from app.schemas.order import OrderCreateRequest, OrderResponse, OrderItemResponse, OrderItemOptionResponse
from app.services.external_client import menu_client, store_client
from app.sse.event_manager import sse_manager


class OrderService:

    async def create_order(
        self, store_id: int, data: OrderCreateRequest
    ) -> OrderResponse:
        """
        주문 생성 전체 플로우:
        1. 세션 유효성 검증
        2. 동시 주문 확인 (pending 있으면 거부)
        3. 메뉴/옵션 가격 검증
        4. 주문 번호 생성
        5. 주문 저장
        6. SSE 이벤트 발행
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 1. 세션 유효성 검증
            session_data = await store_client.validate_session(data.session_id)
            if session_data is None:
                raise ServiceUnavailableError("Store Service에 연결할 수 없습니다.")
            if not session_data.get("is_active", False):
                raise BusinessRuleError("종료된 세션에는 주문할 수 없습니다.")
            if session_data.get("table_id") != data.table_id:
                raise BusinessRuleError("세션과 테이블 정보가 일치하지 않습니다.")

            async with conn.cursor() as cur:
                # 2. 동시 주문 확인
                await cur.execute(
                    q.CHECK_PENDING_ORDER, (data.table_id, data.session_id)
                )
                pending = await cur.fetchone()
                if pending:
                    raise PendingOrderExistsError(
                        order_id=pending[0],
                        order_number=pending[1],
                        status=pending[2],
                        created_at=str(pending[3]),
                    )

                # 3. 가격 검증
                price_mismatches = []
                validated_items = []

                for item in data.items:
                    menu_data = await menu_client.validate_menu(item.menu_item_id)
                    if menu_data is None:
                        raise ServiceUnavailableError(
                            "Menu Service에 연결할 수 없습니다."
                        )
                    if not menu_data.get("is_available", False):
                        raise BusinessRuleError(
                            f"메뉴 '{item.menu_name}'은(는) 현재 주문할 수 없습니다."
                        )
                    if menu_data["price"] != item.menu_price:
                        price_mismatches.append({
                            "menu_id": item.menu_item_id,
                            "current_price": menu_data["price"],
                            "submitted_price": item.menu_price,
                        })

                    # 옵션 가격도 검증
                    option_map = {}
                    for og in menu_data.get("option_groups", []):
                        for opt in og.get("options", []):
                            option_map[opt["id"]] = opt["price"]

                    for opt in item.options:
                        if opt.option_item_id in option_map:
                            if option_map[opt.option_item_id] != opt.option_price:
                                price_mismatches.append({
                                    "menu_id": item.menu_item_id,
                                    "current_price": option_map[opt.option_item_id],
                                    "submitted_price": opt.option_price,
                                })

                    validated_items.append(item)

                if price_mismatches:
                    raise PriceMismatchError(price_mismatches)

                # 4. 주문 번호 생성
                await cur.execute(q.GET_LAST_ORDER_NUMBER_TODAY, (store_id,))
                last_row = await cur.fetchone()
                if last_row and last_row[0]:
                    next_num = int(last_row[0]) + 1
                else:
                    next_num = 1
                order_number = str(next_num).zfill(3)

                # 5. 주문 저장 (트랜잭션)
                # 총액 계산
                total_amount = 0
                for item in data.items:
                    option_total = sum(opt.option_price for opt in item.options)
                    subtotal = (item.menu_price + option_total) * item.quantity
                    total_amount += subtotal

                await cur.execute(
                    q.INSERT_ORDER,
                    (store_id, data.table_id, data.session_id, order_number, total_amount),
                )
                order_id = cur.lastrowid

                # 주문 항목 저장
                for item in data.items:
                    option_total = sum(opt.option_price for opt in item.options)
                    subtotal = (item.menu_price + option_total) * item.quantity

                    await cur.execute(
                        q.INSERT_ORDER_ITEM,
                        (order_id, item.menu_item_id, item.menu_name,
                         item.menu_price, item.quantity, subtotal),
                    )
                    item_id = cur.lastrowid

                    # 옵션 저장
                    for opt in item.options:
                        await cur.execute(
                            q.INSERT_ORDER_ITEM_OPTION,
                            (item_id, opt.option_item_id, opt.option_name, opt.option_price),
                        )

                await conn.commit()

                # 생성된 주문 조회
                order_response = await self._get_order_with_items(cur, order_id)

        # 6. SSE 이벤트 발행
        await sse_manager.broadcast(store_id, "new_order", order_response.model_dump())

        return order_response

    async def list_orders(
        self,
        store_id: int,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[OrderResponse], int]:
        """매장 전체 주문 목록 (페이지네이션)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                status_filter = f"AND status = '{status}'" if status else ""
                offset = (page - 1) * size

                # 총 개수
                count_query = q.COUNT_ORDERS_BY_STORE.format(status_filter=status_filter)
                await cur.execute(count_query, (store_id,))
                count_row = await cur.fetchone()
                total = count_row[0]

                # 주문 목록
                list_query = q.LIST_ORDERS_BY_STORE.format(status_filter=status_filter)
                await cur.execute(list_query, (store_id, size, offset))
                rows = await cur.fetchall()
                orders = [map_order(row) for row in rows]

                # 각 주문의 항목 조회
                results = []
                for order in orders:
                    order_resp = await self._get_order_with_items(cur, order.id)
                    results.append(order_resp)

                return results, total

    async def list_table_orders(
        self, table_id: int, session_id: int
    ) -> list[OrderResponse]:
        """테이블 세션 내 주문 목록"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    q.LIST_ORDERS_BY_TABLE_SESSION, (table_id, session_id)
                )
                rows = await cur.fetchall()
                orders = [map_order(row) for row in rows]

                results = []
                for order in orders:
                    order_resp = await self._get_order_with_items(cur, order.id)
                    results.append(order_resp)

                return results

    async def list_active_orders(self, store_id: int) -> list[OrderResponse]:
        """활성 주문 목록 (SSE 초기 데이터)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.LIST_ACTIVE_ORDERS, (store_id,))
                rows = await cur.fetchall()
                orders = [map_order(row) for row in rows]

                results = []
                for order in orders:
                    order_resp = await self._get_order_with_items(cur, order.id)
                    results.append(order_resp)

                return results

    async def update_order_status(
        self, order_id: int, new_status: str
    ) -> OrderResponse:
        """주문 상태 변경 (자유 전이)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_ORDER_BY_ID, (order_id,))
                row = await cur.fetchone()
                if not row:
                    raise NotFoundError("주문을 찾을 수 없습니다.")

                order = map_order(row)
                old_status = order.status

                await cur.execute(q.UPDATE_ORDER_STATUS, (new_status, order_id))
                await conn.commit()

                order_resp = await self._get_order_with_items(cur, order_id)

        # SSE 이벤트
        await sse_manager.broadcast(
            order.store_id,
            "status_changed",
            {
                "order_id": order_id,
                "table_id": order.table_id,
                "old_status": old_status,
                "new_status": new_status,
                "updated_at": order_resp.updated_at.isoformat(),
            },
        )

        return order_resp

    async def delete_order(self, order_id: int) -> dict:
        """주문 삭제 (하드 삭제, cascade)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q.GET_ORDER_BY_ID, (order_id,))
                row = await cur.fetchone()
                if not row:
                    raise NotFoundError("주문을 찾을 수 없습니다.")

                order = map_order(row)

                # 삭제 전 전체 정보 조회 (SSE 이벤트용)
                order_resp = await self._get_order_with_items(cur, order_id)
                deleted_data = order_resp.model_dump()

                await cur.execute(q.DELETE_ORDER, (order_id,))
                await conn.commit()

        # SSE 이벤트 (전체 정보 포함)
        from datetime import datetime
        deleted_data["deleted_at"] = datetime.now().isoformat()
        await sse_manager.broadcast(order.store_id, "order_deleted", deleted_data)

        return deleted_data

    async def archive_session_orders(self, session_id: int, store_id: int) -> int:
        """세션 주문 아카이브 (상태 무관 모두 이동)"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 세션의 모든 주문 조회
                await cur.execute(q.LIST_ORDERS_BY_SESSION, (session_id,))
                rows = await cur.fetchall()
                orders = [map_order(row) for row in rows]

                if not orders:
                    return 0

                # 각 주문을 아카이브
                for order in orders:
                    # 항목 + 옵션 JSON 직렬화
                    order_resp = await self._get_order_with_items(cur, order.id)
                    items_snapshot = json.dumps(
                        [item.model_dump() for item in order_resp.items],
                        ensure_ascii=False,
                        default=str,
                    )

                    await cur.execute(
                        q.INSERT_ORDER_HISTORY,
                        (
                            order.id,
                            order.store_id,
                            order.table_id,
                            order.session_id,
                            order.order_number,
                            order.status,
                            order.total_amount,
                            items_snapshot,
                            order.created_at,
                        ),
                    )

                # 원본 삭제 (cascade로 items/options도 삭제)
                await cur.execute(q.DELETE_ORDERS_BY_SESSION, (session_id,))
                await conn.commit()

                return len(orders)

    async def get_order_history(
        self,
        store_id: int,
        table_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[OrderHistory], int]:
        """과거 주문 이력 조회"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                date_filter = ""
                if date_from:
                    date_filter += f" AND archived_at >= '{date_from}'"
                if date_to:
                    date_filter += f" AND archived_at <= '{date_to} 23:59:59'"

                offset = (page - 1) * size

                count_query = q.COUNT_ORDER_HISTORY.format(date_filter=date_filter)
                await cur.execute(count_query, (store_id, table_id))
                count_row = await cur.fetchone()
                total = count_row[0]

                list_query = q.LIST_ORDER_HISTORY.format(date_filter=date_filter)
                await cur.execute(list_query, (store_id, table_id, size, offset))
                rows = await cur.fetchall()
                histories = [map_order_history(row) for row in rows]

                return histories, total

    async def _get_order_with_items(self, cur, order_id: int) -> OrderResponse:
        """주문 + 항목 + 옵션 전체 조회"""
        await cur.execute(q.GET_ORDER_BY_ID, (order_id,))
        order_row = await cur.fetchone()
        order = map_order(order_row)

        # 항목 조회
        await cur.execute(q.LIST_ORDER_ITEMS, (order_id,))
        item_rows = await cur.fetchall()
        items = [map_order_item(row) for row in item_rows]

        # 옵션 조회
        item_responses = []
        if items:
            item_ids = [i.id for i in items]
            placeholders = ",".join(["%s"] * len(item_ids))
            opt_query = q.LIST_ORDER_ITEM_OPTIONS.format(placeholders=placeholders)
            await cur.execute(opt_query, item_ids)
            opt_rows = await cur.fetchall()
            options = [map_order_item_option(row) for row in opt_rows]

            options_by_item: dict[int, list[OrderItemOption]] = {}
            for opt in options:
                options_by_item.setdefault(opt.order_item_id, []).append(opt)

            for item in items:
                item_opts = options_by_item.get(item.id, [])
                item_responses.append(
                    OrderItemResponse(
                        id=item.id,
                        order_id=item.order_id,
                        menu_item_id=item.menu_item_id,
                        menu_name=item.menu_name,
                        menu_price=item.menu_price,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        options=[
                            OrderItemOptionResponse(**o.__dict__) for o in item_opts
                        ],
                        created_at=item.created_at,
                    )
                )

        return OrderResponse(
            id=order.id,
            store_id=order.store_id,
            table_id=order.table_id,
            session_id=order.session_id,
            order_number=order.order_number,
            status=order.status,
            total_amount=order.total_amount,
            items=item_responses,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


# Custom Exceptions
class BusinessRuleError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ServiceUnavailableError(Exception):
    pass


class PriceMismatchError(Exception):
    def __init__(self, mismatches: list[dict]):
        self.mismatches = mismatches
        super().__init__("가격 불일치")


class PendingOrderExistsError(Exception):
    def __init__(self, order_id: int, order_number: str, status: str, created_at: str):
        self.existing_order = {
            "order_id": order_id,
            "order_number": order_number,
            "status": status,
            "created_at": created_at,
        }
        super().__init__("대기 중인 주문이 존재합니다.")
