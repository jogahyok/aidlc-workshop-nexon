# 컴포넌트 메서드 정의

## 1. Auth Service

### API Endpoints
| Method | Path | Purpose | Input | Output |
|--------|------|---------|-------|--------|
| POST | /auth/admin/login | 관리자 로그인 | store_id, username, password | access_token, expires_at |
| POST | /auth/admin/refresh | 토큰 갱신 | refresh_token | access_token |
| POST | /auth/table/login | 테이블 태블릿 로그인 | store_id, table_number, password | access_token, table_info |
| GET | /auth/me | 현재 인증 정보 조회 | (token) | user_info |

### Service Methods
- `authenticate_admin(store_id, username, password) -> TokenPair`
- `authenticate_table(store_id, table_number, password) -> TableToken`
- `verify_token(token) -> TokenPayload`
- `check_login_attempts(store_id, username) -> bool`

---

## 2. Store Service

### API Endpoints
| Method | Path | Purpose | Input | Output |
|--------|------|---------|-------|--------|
| GET | /stores/{store_id} | 매장 정보 조회 | store_id | store_info |
| GET | /stores/{store_id}/tables | 테이블 목록 조회 | store_id | table_list |
| POST | /stores/{store_id}/tables | 테이블 등록 | table_number, password | table_info |
| PUT | /stores/{store_id}/tables/{table_id} | 테이블 수정 | table_data | table_info |
| POST | /stores/{store_id}/tables/{table_id}/complete | 테이블 이용 완료 | table_id | success |
| GET | /stores/{store_id}/tables/{table_id}/session | 현재 세션 조회 | table_id | session_info |

### Service Methods
- `get_store(store_id) -> Store`
- `list_tables(store_id) -> List[Table]`
- `create_table(store_id, table_number, password) -> Table`
- `complete_table_session(store_id, table_id) -> Session`
- `get_current_session(table_id) -> Optional[TableSession]`
- `start_new_session(table_id) -> TableSession`

---

## 3. Menu Service

### API Endpoints
| Method | Path | Purpose | Input | Output |
|--------|------|---------|-------|--------|
| GET | /stores/{store_id}/categories | 카테고리 목록 | store_id | category_list |
| POST | /stores/{store_id}/categories | 카테고리 생성 | name, sort_order | category |
| PUT | /categories/{category_id} | 카테고리 수정 | name, sort_order | category |
| DELETE | /categories/{category_id} | 카테고리 삭제 | category_id | success |
| GET | /stores/{store_id}/menus | 메뉴 목록 | store_id, category_id? | menu_list |
| POST | /stores/{store_id}/menus | 메뉴 등록 | menu_data | menu_item |
| PUT | /menus/{menu_id} | 메뉴 수정 | menu_data | menu_item |
| DELETE | /menus/{menu_id} | 메뉴 삭제 | menu_id | success |
| POST | /menus/{menu_id}/image | 이미지 업로드 URL 발급 | menu_id, content_type | presigned_url |
| GET | /menus/{menu_id}/options | 옵션 그룹 조회 | menu_id | option_groups |
| POST | /menus/{menu_id}/options | 옵션 그룹 생성 | group_data | option_group |
| PUT | /option-groups/{group_id} | 옵션 그룹 수정 | group_data | option_group |
| DELETE | /option-groups/{group_id} | 옵션 그룹 삭제 | group_id | success |

### Service Methods
- `list_categories(store_id) -> List[Category]`
- `create_menu_item(store_id, menu_data) -> MenuItem`
- `update_menu_item(menu_id, menu_data) -> MenuItem`
- `delete_menu_item(menu_id) -> None`
- `generate_upload_url(menu_id, content_type) -> str`
- `create_option_group(menu_id, group_data) -> OptionGroup`
- `update_option_group(group_id, group_data) -> OptionGroup`

---

## 4. Order Service

### API Endpoints
| Method | Path | Purpose | Input | Output |
|--------|------|---------|-------|--------|
| POST | /stores/{store_id}/orders | 주문 생성 | table_id, session_id, items | order |
| GET | /stores/{store_id}/orders | 주문 목록 (관리자) | store_id, status? | order_list |
| GET | /stores/{store_id}/tables/{table_id}/orders | 테이블 주문 조회 | table_id, session_id | order_list |
| PATCH | /orders/{order_id}/status | 주문 상태 변경 | status | order |
| DELETE | /orders/{order_id} | 주문 삭제 (관리자) | order_id | success |
| GET | /stores/{store_id}/tables/{table_id}/history | 과거 주문 이력 | table_id, date_from?, date_to? | history_list |
| GET | /stores/{store_id}/orders/stream | SSE 실시간 주문 스트림 | store_id | EventStream |

### Service Methods
- `create_order(store_id, table_id, session_id, items) -> Order`
- `list_orders(store_id, status_filter?) -> List[Order]`
- `list_table_orders(table_id, session_id) -> List[Order]`
- `update_order_status(order_id, new_status) -> Order`
- `delete_order(order_id) -> None`
- `get_order_history(table_id, date_from?, date_to?) -> List[OrderHistory]`
- `archive_session_orders(session_id) -> None`
- `stream_orders(store_id) -> AsyncGenerator[OrderEvent]`

---

## 5. API Gateway

### 기능
- 요청 라우팅 (path prefix 기반)
- JWT 토큰 검증 미들웨어
- CORS 정책 적용
- Rate Limiting
- HTTP 보안 헤더 주입
- 요청/응답 로깅

---

## 6. Customer App (주요 컴포넌트)

| 컴포넌트 | 책임 |
|----------|------|
| AuthProvider | 자동 로그인 상태 관리, 토큰 저장 |
| MenuPage | 카테고리/메뉴 목록 표시 |
| MenuOptionModal | 메뉴 옵션 선택 UI |
| CartProvider | 장바구니 상태 관리 (Context + useReducer) |
| CartPage | 장바구니 내용 표시, 수량 조절 |
| OrderConfirmPage | 주문 최종 확인 |
| OrderHistoryPage | 주문 내역 목록 |

---

## 7. Admin App (주요 컴포넌트)

| 컴포넌트 | 책임 |
|----------|------|
| AuthProvider | 관리자 로그인 상태 관리 |
| LoginPage | 로그인 폼 |
| OrderDashboard | 테이블별 그리드 주문 현황 (SSE) |
| OrderDetailModal | 주문 상세 보기, 상태 변경 |
| TableManagement | 테이블 설정, 세션 관리 |
| MenuManagement | 메뉴 CRUD, 옵션 관리 |
| OrderHistoryModal | 과거 주문 내역 조회 |

---

## 8. Shared UI Library

| 모듈 | 포함 항목 |
|------|-----------|
| components | Button, Card, Modal, Loading, Toast, Input, Select |
| hooks | useApi, useAuth, useLocalStorage |
| types | Store, Table, MenuItem, Order, OptionGroup 등 공통 타입 |
| utils | formatPrice, formatDate, apiClient |
