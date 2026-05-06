# 비즈니스 로직 상세 설계 — Menu Service + Order Service (개발자 B)

## 설계 결정 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| 가격 검증 범위 | 0원 이상 허용 | 무료 메뉴(서비스 메뉴, 이벤트) 지원 |
| 메뉴 삭제 방식 | 소프트 삭제 (is_deleted) | 기존 주문에서 메뉴 정보 조회 가능 유지 |
| 가격 검증 실패 처리 | 주문 거부 + 최신 가격 반환 | 고객에게 정확한 정보 제공, 재주문 유도 |
| 주문 상태 전이 | 자유 전이 | 운영 유연성 확보 (실수 복구 가능) |
| SSE 전략 | 매장별 단일 스트림 | 구현 단순, 관리 용이 |
| 아카이브 방식 | 복사 후 원본 삭제 | 명확한 데이터 분리, 조회 성능 유지 |
| 옵션 그룹 타입 | 단일 선택(라디오) + 다중 선택(체크박스) | 직관적 UI 매핑, 명확한 선택 규칙 |

---

## Part 1: Menu Service 비즈니스 로직

### 1.1 도메인 엔티티

#### Category (카테고리)
```python
class Category:
    id: int                  # PK, auto-increment
    store_id: int            # FK → stores.id
    name: str                # 카테고리명 (필수, 1~50자)
    sort_order: int          # 노출 순서 (0부터 시작)
    created_at: datetime
    updated_at: datetime
```

#### MenuItem (메뉴 항목)
```python
class MenuItem:
    id: int                  # PK, auto-increment
    store_id: int            # FK → stores.id
    category_id: int         # FK → categories.id
    name: str                # 메뉴명 (필수, 1~100자)
    description: str         # 설명 (선택, 최대 500자)
    price: int               # 가격 (0 이상, 단위: 원)
    image_url: str | None    # S3 이미지 URL
    sort_order: int          # 카테고리 내 노출 순서
    is_deleted: bool         # 소프트 삭제 플래그 (기본: False)
    created_at: datetime
    updated_at: datetime
```

#### OptionGroup (옵션 그룹)
```python
class OptionGroup:
    id: int                  # PK, auto-increment
    menu_item_id: int        # FK → menu_items.id
    name: str                # 그룹명 (예: "사이즈", "토핑")
    type: str                # "radio" (단일 선택) | "checkbox" (다중 선택)
    is_required: bool        # 필수 여부 (radio는 항상 True)
    max_select: int | None   # 최대 선택 수 (checkbox용, None=무제한)
    sort_order: int          # 옵션 그룹 노출 순서
    created_at: datetime
    updated_at: datetime
```

#### OptionItem (옵션 항목)
```python
class OptionItem:
    id: int                  # PK, auto-increment
    option_group_id: int     # FK → option_groups.id
    name: str                # 옵션명 (예: "라지", "치즈 추가")
    price: int               # 추가 가격 (0 이상)
    sort_order: int          # 옵션 항목 노출 순서
    created_at: datetime
    updated_at: datetime
```

---

### 1.2 비즈니스 규칙

#### 카테고리 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| CAT-001 | 카테고리명은 같은 매장 내에서 유일해야 한다 | 409 Conflict |
| CAT-002 | 카테고리 삭제 시 하위 메뉴가 있으면 삭제 불가 | 400 Bad Request |
| CAT-003 | sort_order는 같은 매장 내에서 유일해야 한다 | 자동 재정렬 |

#### 메뉴 항목 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| MENU-001 | 가격은 0원 이상이어야 한다 | 422 Validation Error |
| MENU-002 | 메뉴명은 필수이며 1~100자 | 422 Validation Error |
| MENU-003 | 삭제는 소프트 삭제 (is_deleted=True) | - |
| MENU-004 | 소프트 삭제된 메뉴는 목록 조회에서 제외 | - |
| MENU-005 | 소프트 삭제된 메뉴의 옵션 그룹도 조회에서 제외 | - |
| MENU-006 | category_id는 같은 매장의 유효한 카테고리여야 한다 | 404 Not Found |

#### 옵션 그룹 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| OPT-001 | type은 "radio" 또는 "checkbox"만 허용 | 422 Validation Error |
| OPT-002 | radio 타입은 is_required=True 고정 | 자동 설정 |
| OPT-003 | radio 타입은 max_select=1 고정 | 자동 설정 |
| OPT-004 | checkbox 타입의 max_select는 1 이상이거나 None(무제한) | 422 Validation Error |
| OPT-005 | 옵션 항목 가격은 0원 이상 | 422 Validation Error |
| OPT-006 | 메뉴 소프트 삭제 시 옵션 그룹/항목은 유지 (조회만 제외) | - |

#### 이미지 업로드 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| IMG-001 | 허용 content_type: image/jpeg, image/png, image/webp | 400 Bad Request |
| IMG-002 | Presigned URL 유효 시간: 10분 | - |
| IMG-003 | 업로드 완료 후 menu_items.image_url 업데이트 | - |

---

### 1.3 내부 API: 가격 검증

**엔드포인트**: `GET /internal/menus/{menu_id}/validate`

**목적**: Order Service가 주문 생성 시 메뉴/옵션의 현재 가격을 검증

**응답 구조**:
```json
{
  "menu_id": 1,
  "name": "아메리카노",
  "price": 4500,
  "is_available": true,
  "option_groups": [
    {
      "id": 1,
      "name": "사이즈",
      "type": "radio",
      "options": [
        {"id": 1, "name": "레귤러", "price": 0},
        {"id": 2, "name": "라지", "price": 500}
      ]
    }
  ]
}
```

**검증 로직**:
- is_deleted=True인 메뉴 → `is_available: false`
- 존재하지 않는 menu_id → 404 Not Found

---

### 1.4 DB 스키마

```sql
-- categories 테이블
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_store_name (store_id, name),
    UNIQUE KEY uk_store_sort (store_id, sort_order)
);

-- menu_items 테이블
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    price INT NOT NULL DEFAULT 0,
    image_url VARCHAR(512),
    sort_order INT NOT NULL DEFAULT 0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_category (store_id, category_id),
    INDEX idx_store_deleted (store_id, is_deleted),
    CONSTRAINT chk_price CHECK (price >= 0)
);

-- option_groups 테이블
CREATE TABLE option_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    type ENUM('radio', 'checkbox') NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    max_select INT,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_menu_item (menu_item_id)
);

-- option_items 테이블
CREATE TABLE option_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    option_group_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    price INT NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_option_group (option_group_id),
    CONSTRAINT chk_option_price CHECK (price >= 0)
);
```

---

## Part 2: Order Service 비즈니스 로직

### 2.1 도메인 엔티티

#### Order (주문)
```python
class Order:
    id: int                  # PK, auto-increment
    store_id: int            # FK → stores.id
    table_id: int            # FK → tables.id
    session_id: int          # FK → table_sessions.id
    order_number: str        # 주문 번호 (매장 내 일련번호, 예: "001")
    status: str              # "pending" | "preparing" | "completed"
    total_amount: int        # 총 주문 금액 (계산된 값)
    created_at: datetime
    updated_at: datetime
```

#### OrderItem (주문 항목)
```python
class OrderItem:
    id: int                  # PK, auto-increment
    order_id: int            # FK → orders.id
    menu_item_id: int        # 원본 메뉴 ID (참조용)
    menu_name: str           # 주문 시점 메뉴명 (스냅샷)
    menu_price: int          # 주문 시점 단가 (스냅샷)
    quantity: int            # 수량 (1 이상)
    subtotal: int            # 소계 = (menu_price + 옵션 합계) × quantity
    created_at: datetime
```

#### OrderItemOption (주문 항목 옵션)
```python
class OrderItemOption:
    id: int                  # PK, auto-increment
    order_item_id: int       # FK → order_items.id
    option_item_id: int      # 원본 옵션 ID (참조용)
    option_name: str         # 주문 시점 옵션명 (스냅샷)
    option_price: int        # 주문 시점 옵션 가격 (스냅샷)
    created_at: datetime
```

#### OrderHistory (주문 이력)
```python
class OrderHistory:
    id: int                  # PK, auto-increment
    original_order_id: int   # 원본 주문 ID
    store_id: int
    table_id: int
    session_id: int
    order_number: str
    status: str              # 아카이브 시점의 상태
    total_amount: int
    items_snapshot: str      # JSON 직렬화된 주문 항목 전체
    ordered_at: datetime     # 원본 주문 생성 시각
    archived_at: datetime    # 아카이브 시각
```

---

### 2.2 비즈니스 규칙

#### 주문 생성 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| ORD-001 | 주문 항목은 1개 이상이어야 한다 | 400 Bad Request |
| ORD-002 | 각 항목의 수량은 1 이상이어야 한다 | 422 Validation Error |
| ORD-003 | 메뉴 가격은 Menu Service에서 실시간 검증 | 가격 불일치 시 주문 거부 |
| ORD-004 | 삭제된 메뉴(is_available=false)는 주문 불가 | 400 Bad Request |
| ORD-005 | radio 타입 옵션 그룹은 정확히 1개 선택 필수 | 422 Validation Error |
| ORD-006 | checkbox 타입은 max_select 이하로 선택 | 422 Validation Error |
| ORD-007 | 주문 생성 시 status는 "pending"으로 고정 | - |
| ORD-008 | order_number는 매장 내 당일 일련번호 자동 생성 | - |

#### 가격 검증 플로우
```
1. 클라이언트가 주문 요청 (items: [{menu_id, quantity, options: [option_id, ...]}])
2. Order Service → Menu Service: GET /internal/menus/{menu_id}/validate
3. 응답의 price와 클라이언트 전송 가격 비교
4. 불일치 시:
   - 주문 거부 (HTTP 409 Conflict)
   - 응답에 최신 가격 정보 포함
   {
     "error": "PRICE_MISMATCH",
     "message": "메뉴 가격이 변경되었습니다. 최신 가격을 확인해 주세요.",
     "updated_items": [
       {"menu_id": 1, "current_price": 5000, "submitted_price": 4500}
     ]
   }
5. 일치 시: 주문 생성 진행
```

#### 금액 계산 규칙
```
주문 항목 소계 = (메뉴 단가 + Σ(선택 옵션 가격)) × 수량
주문 총액 = Σ(모든 주문 항목 소계)
```

#### 주문 상태 전이 규칙 (자유 전이)
```
+----------+     +-----------+     +-----------+
| pending  | <-> | preparing | <-> | completed |
+----------+     +-----------+     +-----------+
     ^                                    |
     +------------------------------------+
```

| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| STS-001 | 유효한 상태값: "pending", "preparing", "completed" | 422 Validation Error |
| STS-002 | 모든 상태 간 자유 전이 허용 | - |
| STS-003 | 상태 변경 시 updated_at 갱신 | - |
| STS-004 | 상태 변경 시 SSE 이벤트 발행 | - |

#### 주문 삭제 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| DEL-001 | 관리자 권한만 삭제 가능 | 403 Forbidden |
| DEL-002 | 삭제는 하드 삭제 (DB에서 완전 제거) | - |
| DEL-003 | 삭제 시 order_items, order_item_options도 cascade 삭제 | - |
| DEL-004 | 삭제 시 SSE 이벤트 발행 (order_deleted) | - |

#### 주문 이력 아카이브 규칙
| 규칙 ID | 규칙 | 위반 시 |
|---------|------|---------|
| ARC-001 | Store Service의 세션 종료 요청으로만 트리거 | - |
| ARC-002 | 해당 session_id의 모든 주문을 아카이브 | - |
| ARC-003 | 주문 항목 전체를 JSON으로 직렬화하여 items_snapshot에 저장 | - |
| ARC-004 | order_history INSERT 후 원본 orders/order_items/order_item_options DELETE | - |
| ARC-005 | INSERT + DELETE는 단일 트랜잭션으로 처리 | - |
| ARC-006 | 아카이브 완료 후 SSE 이벤트 발행하지 않음 (Store Service가 처리) | - |

---

### 2.3 SSE (Server-Sent Events) 설계

#### 이벤트 타입
| 이벤트 | 트리거 | 페이로드 |
|--------|--------|----------|
| `new_order` | 주문 생성 완료 | order 전체 정보 (items 포함) |
| `status_changed` | 주문 상태 변경 | {order_id, table_id, old_status, new_status, updated_at} |
| `order_deleted` | 주문 삭제 | {order_id, table_id, deleted_at} |

#### 연결 관리
```python
# 매장별 SSE 연결 관리
class SSEEventManager:
    # store_id → List[SSE Connection]
    connections: dict[int, list[SSEConnection]]
    
    async def connect(store_id: int, connection: SSEConnection):
        """새 SSE 연결 등록"""
        
    async def disconnect(store_id: int, connection: SSEConnection):
        """SSE 연결 해제"""
        
    async def broadcast(store_id: int, event: SSEEvent):
        """매장의 모든 연결에 이벤트 전송"""
        
    async def heartbeat():
        """30초마다 ping 이벤트 전송 (연결 유지)"""
```

#### SSE 엔드포인트
```
GET /stores/{store_id}/orders/stream
Headers:
  Accept: text/event-stream
  Authorization: Bearer {admin_token}

Response (text/event-stream):
  event: new_order
  data: {"order_id": 1, "table_id": 3, ...}
  
  event: status_changed
  data: {"order_id": 1, "old_status": "pending", "new_status": "preparing"}
  
  event: heartbeat
  data: {"timestamp": "2026-05-06T10:00:00Z"}
```

#### 재연결 처리
- 클라이언트 측 `EventSource` 자동 재연결 활용
- `Last-Event-ID` 헤더는 미지원 (재연결 시 현재 상태만 제공)
- 재연결 시 초기 데이터: 현재 활성 주문 목록 전송

---

### 2.4 외부 연동

#### Order → Menu Service (가격 검증)
```python
async def validate_menu_price(menu_id: int) -> MenuValidation:
    """
    Menu Service 내부 API 호출
    - URL: GET http://menu-service/internal/menus/{menu_id}/validate
    - Timeout: 5초
    - 실패 시: 주문 거부 (503 Service Unavailable)
    - 재시도: 1회 (총 2회 시도)
    """
```

#### Store → Order Service (아카이브 요청 수신)
```python
# POST /internal/orders/archive
# Request Body:
{
    "session_id": 123,
    "store_id": 1
}

# Response (성공):
{
    "archived_count": 5,
    "session_id": 123
}

# Response (실패):
{
    "error": "ARCHIVE_FAILED",
    "message": "아카이브 처리 중 오류가 발생했습니다."
}
```

---

### 2.5 DB 스키마

```sql
-- orders 테이블
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    table_id INT NOT NULL,
    session_id INT NOT NULL,
    order_number VARCHAR(10) NOT NULL,
    status ENUM('pending', 'preparing', 'completed') NOT NULL DEFAULT 'pending',
    total_amount INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_status (store_id, status),
    INDEX idx_table_session (table_id, session_id),
    INDEX idx_store_created (store_id, created_at),
    CONSTRAINT chk_total CHECK (total_amount >= 0)
);

-- order_items 테이블
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    menu_name VARCHAR(100) NOT NULL,
    menu_price INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    subtotal INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order (order_id),
    CONSTRAINT chk_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_subtotal CHECK (subtotal >= 0),
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- order_item_options 테이블
CREATE TABLE order_item_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    option_item_id INT NOT NULL,
    option_name VARCHAR(50) NOT NULL,
    option_price INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_item (order_item_id),
    CONSTRAINT chk_opt_price CHECK (option_price >= 0),
    CONSTRAINT fk_order_item FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE
);

-- order_history 테이블
CREATE TABLE order_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_order_id INT NOT NULL,
    store_id INT NOT NULL,
    table_id INT NOT NULL,
    session_id INT NOT NULL,
    order_number VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount INT NOT NULL,
    items_snapshot JSON NOT NULL,
    ordered_at DATETIME NOT NULL,
    archived_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_store_table (store_id, table_id),
    INDEX idx_session (session_id),
    INDEX idx_archived (store_id, archived_at)
);
```

---

## Part 3: 서비스 간 연동 및 에러 시나리오

### 3.1 Menu ↔ Order 가격 검증 연동

```
[Order Service]                    [Menu Service]
     |                                   |
     |  GET /internal/menus/1/validate   |
     |---------------------------------->|
     |                                   |
     |  200 OK {price: 4500, ...}        |
     |<----------------------------------|
     |                                   |
     |  가격 비교                         |
     |  일치 → 주문 생성                  |
     |  불일치 → 409 Conflict 반환        |
```

### 3.2 Store → Order 아카이브 연동

```
[Store Service]                    [Order Service]
     |                                   |
     |  POST /internal/orders/archive    |
     |  {session_id: 123}               |
     |---------------------------------->|
     |                                   |
     |                          [트랜잭션 시작]
     |                          1. session_id로 주문 조회
     |                          2. 각 주문을 JSON 직렬화
     |                          3. order_history INSERT
     |                          4. 원본 주문 DELETE
     |                          [트랜잭션 커밋]
     |                                   |
     |  200 OK {archived_count: 5}       |
     |<----------------------------------|
```

### 3.3 에러 시나리오

| 시나리오 | 발생 조건 | 처리 방식 |
|----------|-----------|-----------|
| Menu Service 응답 없음 | 가격 검증 시 timeout (5초) | 1회 재시도 후 503 반환 |
| Menu Service 404 | 존재하지 않는 menu_id | 주문 거부 (400 Bad Request) |
| 가격 불일치 | 클라이언트 가격 ≠ 서버 가격 | 409 Conflict + 최신 가격 반환 |
| 아카이브 중 DB 오류 | INSERT/DELETE 실패 | 트랜잭션 롤백, 500 반환 |
| SSE 연결 끊김 | 네트워크 오류 | 클라이언트 자동 재연결 |
| 동시 상태 변경 | 같은 주문 동시 업데이트 | 낙관적 잠금 (updated_at 비교) |

---

## Part 4: 공통 패턴

### 4.1 에러 응답 형식
```json
{
  "error": "ERROR_CODE",
  "message": "사용자 친화적 메시지",
  "details": {}  // 선택적 추가 정보
}
```

### 4.2 표준 HTTP 상태 코드
| 코드 | 용도 |
|------|------|
| 200 | 성공 (조회, 수정) |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 (비즈니스 규칙 위반) |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 충돌 (가격 불일치, 중복) |
| 422 | 유효성 검증 실패 |
| 500 | 서버 내부 오류 |
| 503 | 외부 서비스 불가 |

### 4.3 페이지네이션
```json
// Request: GET /stores/1/orders?page=1&size=20
// Response:
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "total_pages": 8
}
```

---

## 다음 단계

이 문서를 기반으로 실제 구현을 진행합니다:
1. DB 마이그레이션 스크립트 작성
2. 도메인 모델 코드 구현
3. 서비스 레이어 구현
4. API 라우트 구현
5. 단위 테스트 + PBT 작성
6. Swagger 문서 자동 생성 확인
