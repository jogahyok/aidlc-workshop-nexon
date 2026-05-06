# 비즈니스 로직 상세 설계 v2 — Menu Service + Order Service (개발자 B)

> 이 문서는 기존 `menu-order-business-logic.md`의 보완 버전입니다.
> 추가 질문(Q8~Q24) 답변을 반영하여 누락된 규칙과 API를 추가했습니다.

---

## 전체 설계 결정 요약 (Q1~Q24)

| # | 항목 | 결정 |
|---|------|------|
| 1 | 가격 검증 범위 | 0원 이상 허용 (무료 메뉴 가능) |
| 2 | 메뉴 삭제 방식 | 소프트 삭제 (is_deleted) |
| 3 | 가격 검증 실패 | 주문 거부 + 최신 가격 반환 |
| 4 | 주문 상태 전이 | 자유 전이 (모든 방향 허용) |
| 5 | SSE 전략 | 매장별 단일 스트림 |
| 6 | 아카이브 방식 | order_history로 복사 후 원본 삭제 |
| 7 | 옵션 그룹 타입 | 단일 선택(radio) + 다중 선택(checkbox) |
| 8 | 카테고리 삭제 | 하위 메뉴도 cascade 소프트 삭제 |
| 9 | 메뉴 정렬 | sort_order 기본 + 가격순/이름순 파라미터 |
| 10 | 순서 변경 | 위/아래 이동 API |
| 11 | 옵션 없는 메뉴 | 옵션 유무에 따라 자동 분기 |
| 12 | 이미지 없음 표시 | 회색 플레이스홀더 + "이미지 없음" |
| 13 | 소프트 삭제 복구 | 복구 기능 제공 (관리자) |
| 14 | 주문 번호 | 매장 내 당일 일련번호 (매일 리셋) |
| 15 | 세션 검증 | Store Service에 HTTP 호출로 확인 |
| 16 | 동시 주문 | pending 주문 있으면 새 주문 불가 |
| 17 | SSE 초기 데이터 | 연결 즉시 활성 주문 전체 전송 |
| 18 | 페이지네이션 | 오프셋 기반 (page, size) |
| 19 | 삭제 SSE 페이로드 | 삭제된 주문 전체 정보 포함 |
| 20 | Menu 장애 fallback | 주문 완전 차단 (가격 검증 필수) |
| 21 | history 반환 형식 | JSON 그대로 반환 |
| 22 | 내부 API 인증 | 별도 인증 없음 (네트워크 격리) |
| 23 | 가격 검증 호출 | 메뉴별 개별 호출 |
| 24 | 아카이브 시 활성 주문 | 상태 무관 모두 아카이브 |

---

## Part 1: Menu Service 보완 사항

### 1.1 추가 비즈니스 규칙

#### 카테고리 삭제 (cascade 소프트 삭제)
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| CAT-004 | 카테고리 삭제 시 하위 메뉴 전체를 is_deleted=True 처리 | cascade |
| CAT-005 | 소프트 삭제된 카테고리는 목록 조회에서 제외 | - |
| CAT-006 | 카테고리에 is_deleted 필드 추가 필요 | 스키마 변경 |

#### 메뉴 복구 기능
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| MENU-007 | 관리자는 삭제된 메뉴 목록을 조회할 수 있다 | GET /stores/{store_id}/menus?deleted=true |
| MENU-008 | 관리자는 삭제된 메뉴를 복구할 수 있다 | POST /menus/{menu_id}/restore |
| MENU-009 | 복구 시 원래 카테고리가 삭제 상태면 "미분류"로 이동 | 카테고리 유효성 확인 |
| MENU-010 | 복구 시 옵션 그룹/항목도 함께 복구 | cascade 복구 |

#### 메뉴 정렬 파라미터
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| MENU-011 | 기본 정렬: sort_order ASC | - |
| MENU-012 | 추가 정렬 옵션: price_asc, price_desc, name_asc, name_desc | query param: sort_by |
| MENU-013 | 카테고리 필터: category_id 파라미터 지원 | query param: category_id |

#### 순서 이동 API
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| MENU-014 | POST /menus/{menu_id}/move — direction: "up" 또는 "down" | - |
| MENU-015 | 첫 번째 항목에서 "up" 요청 시 무시 (에러 아님) | 200 OK 반환 |
| MENU-016 | 마지막 항목에서 "down" 요청 시 무시 (에러 아님) | 200 OK 반환 |
| MENU-017 | 이동 시 인접 항목과 sort_order 값 교환 (swap) | - |

### 1.2 추가 API 엔드포인트

| Method | Path | Purpose | 권한 |
|--------|------|---------|------|
| GET | /stores/{store_id}/menus?deleted=true | 삭제된 메뉴 목록 조회 | 관리자 |
| POST | /menus/{menu_id}/restore | 삭제된 메뉴 복구 | 관리자 |
| POST | /menus/{menu_id}/move | 메뉴 순서 이동 (up/down) | 관리자 |
| POST | /categories/{category_id}/move | 카테고리 순서 이동 (up/down) | 관리자 |

### 1.3 DB 스키마 변경사항

```sql
-- categories 테이블에 is_deleted 추가
ALTER TABLE categories ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE categories ADD INDEX idx_store_deleted (store_id, is_deleted);

-- 기존 UNIQUE KEY 수정 (삭제된 카테고리와 이름 충돌 방지)
-- uk_store_name → 삭제된 항목 제외 조건 필요
-- MySQL에서는 partial index 미지원이므로 애플리케이션 레벨에서 처리
```

### 1.4 옵션 없는 메뉴 처리 (프론트엔드 연동 참고)

```json
// GET /stores/{store_id}/menus 응답에 has_options 필드 추가
{
  "id": 1,
  "name": "아메리카노",
  "price": 4500,
  "has_options": true,   // 옵션 그룹 존재 여부
  "image_url": null,     // null이면 프론트에서 플레이스홀더 표시
  ...
}
```

- `has_options: true` → 프론트엔드에서 옵션 선택 모달 표시
- `has_options: false` → 바로 장바구니에 추가 (수량 선택만)

---

## Part 2: Order Service 보완 사항

### 2.1 추가 비즈니스 규칙

#### 주문 번호 생성 (당일 일련번호)
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| ORD-009 | 주문 번호 형식: 3자리 zero-padded (001, 002, ...) | - |
| ORD-010 | 매일 자정(00:00) 기준 리셋 | 서버 타임존: KST |
| ORD-011 | 당일 마지막 번호 + 1로 생성 | 동시성: SELECT FOR UPDATE |
| ORD-012 | 999 초과 시 4자리로 확장 (1000, 1001, ...) | 예외 케이스 |

```python
async def generate_order_number(store_id: int) -> str:
    """
    당일 해당 매장의 마지막 주문 번호를 조회하여 +1
    - 당일 주문이 없으면 "001"부터 시작
    - SELECT MAX(order_number) FROM orders 
      WHERE store_id = ? AND DATE(created_at) = CURDATE()
      FOR UPDATE
    """
```

#### 세션 유효성 검증
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| ORD-013 | 주문 생성 전 Store Service에 세션 유효성 확인 | HTTP 호출 |
| ORD-014 | 종료된 세션에는 주문 생성 불가 | 400 Bad Request |
| ORD-015 | Store Service 응답 없음 시 주문 차단 | 503 반환 |

```python
async def validate_session(store_id: int, table_id: int, session_id: int) -> bool:
    """
    Store Service 내부 API 호출
    - URL: GET http://store-service/internal/sessions/{session_id}/validate
    - 응답: {"is_active": true/false, "table_id": 3}
    - table_id 일치 여부도 확인
    - Timeout: 3초, 재시도: 1회
    """
```

#### 동시 주문 제한
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| ORD-016 | 같은 테이블+세션에 pending 상태 주문이 있으면 새 주문 불가 | 409 Conflict |
| ORD-017 | 에러 응답에 기존 pending 주문 정보 포함 | 클라이언트 안내용 |

```json
// 409 Conflict 응답
{
  "error": "PENDING_ORDER_EXISTS",
  "message": "이전 주문이 아직 대기 중입니다. 주문이 접수된 후 추가 주문이 가능합니다.",
  "existing_order": {
    "order_id": 42,
    "order_number": "003",
    "status": "pending",
    "created_at": "2026-05-06T14:30:00+09:00"
  }
}
```

#### SSE 초기 데이터
| 규칙 ID | 규칙 | 비고 |
|---------|------|------|
| SSE-001 | 연결 즉시 `initial_data` 이벤트로 활성 주문 전체 전송 | - |
| SSE-002 | 활성 주문 = status IN ('pending', 'preparing') | - |
| SSE-003 | 초기 데이터에는 주문 항목(items) 포함 | - |

```
// SSE 연결 직후 전송
event: initial_data
data: {"orders": [{"id": 1, "table_id": 3, "status": "pending", "items": [...], ...}, ...]}

// 이후 개별 이벤트
event: new_order
data: {...}
```

#### 주문 삭제 SSE 이벤트 (전체 정보 포함)
```json
// event: order_deleted
{
  "order_id": 42,
  "table_id": 3,
  "session_id": 10,
  "order_number": "003",
  "status": "pending",
  "total_amount": 15000,
  "items": [
    {"menu_name": "아메리카노", "quantity": 2, "subtotal": 9000},
    {"menu_name": "카페라떼", "quantity": 1, "subtotal": 6000}
  ],
  "deleted_at": "2026-05-06T15:00:00+09:00"
}
```

### 2.2 추가 외부 연동

#### Order → Store Service (세션 검증)
```
[Order Service]                    [Store Service]
     |                                   |
     |  GET /internal/sessions/123/validate
     |---------------------------------->|
     |                                   |
     |  200 OK {"is_active": true, "table_id": 3}
     |<----------------------------------|
```

**Store Service 내부 API 스펙 (개발자A와 합의 필요)**:
| Method | Path | Purpose |
|--------|------|---------|
| GET | /internal/sessions/{session_id}/validate | 세션 활성 상태 확인 |

**응답**:
```json
{
  "session_id": 123,
  "is_active": true,
  "table_id": 3,
  "store_id": 1,
  "started_at": "2026-05-06T12:00:00+09:00"
}
```

### 2.3 주문 생성 전체 플로우 (보완)

```
클라이언트 → Order Service: POST /stores/{store_id}/orders
  │
  ├─ 1. 입력 유효성 검증 (items 비어있지 않은지, quantity >= 1)
  │
  ├─ 2. 세션 유효성 검증
  │     └─ GET http://store-service/internal/sessions/{session_id}/validate
  │     └─ 실패 시: 400 (세션 종료됨) 또는 503 (Store Service 불가)
  │
  ├─ 3. 동시 주문 확인
  │     └─ SELECT * FROM orders WHERE table_id=? AND session_id=? AND status='pending'
  │     └─ 존재 시: 409 Conflict
  │
  ├─ 4. 메뉴/옵션 가격 검증 (메뉴별 개별 호출)
  │     └─ GET http://menu-service/internal/menus/{menu_id}/validate × N
  │     └─ 가격 불일치 시: 409 Conflict + 최신 가격 반환
  │     └─ Menu Service 불가 시: 503 (주문 차단)
  │
  ├─ 5. 주문 번호 생성
  │     └─ 당일 마지막 번호 + 1 (SELECT FOR UPDATE)
  │
  ├─ 6. 주문 저장 (단일 트랜잭션)
  │     └─ INSERT orders
  │     └─ INSERT order_items (스냅샷 저장)
  │     └─ INSERT order_item_options (스냅샷 저장)
  │
  ├─ 7. SSE 이벤트 발행
  │     └─ event: new_order
  │
  └─ 8. 201 Created 응답 반환
```

### 2.4 아카이브 규칙 보완

```
Store Service → Order Service: POST /internal/orders/archive
  │
  ├─ 1. session_id로 해당 세션의 모든 주문 조회 (상태 무관)
  │     └─ pending, preparing, completed 모두 포함
  │
  ├─ 2. 각 주문의 items + options를 JSON 직렬화
  │
  ├─ 3. 트랜잭션 시작
  │     ├─ INSERT INTO order_history (각 주문별)
  │     └─ DELETE FROM orders WHERE session_id = ? (cascade로 items/options도 삭제)
  │
  └─ 4. 응답: {"archived_count": N, "session_id": 123}
```

### 2.5 페이지네이션 스펙

```
// 요청
GET /stores/{store_id}/orders?page=1&size=20&status=pending

// 응답
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| page | int | 1 | 페이지 번호 (1부터 시작) |
| size | int | 20 | 페이지당 항목 수 (최대 100) |
| status | str? | null | 상태 필터 (pending/preparing/completed) |

---

## Part 3: 개발자A와 합의 필요 사항

Order Service가 Store Service의 내부 API를 호출하므로, 개발자A와 다음 API 계약을 합의해야 합니다:

| API | 호출자 | 목적 | 합의 상태 |
|-----|--------|------|-----------|
| GET /internal/sessions/{session_id}/validate | Order Service | 주문 생성 시 세션 유효성 확인 | ⚠️ 합의 필요 |
| POST /internal/orders/archive | Store Service | 세션 종료 시 주문 아카이브 | ✅ 기존 설계에 포함 |

**개발자A에게 요청할 사항**:
1. `/internal/sessions/{session_id}/validate` 엔드포인트 구현
2. 응답 형식: `{session_id, is_active, table_id, store_id, started_at}`
3. 종료된 세션도 조회 가능해야 함 (is_active: false 반환)

---

## Part 4: 수정된 DB 스키마 (최종)

### categories 테이블 (수정)
```sql
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_active (store_id, is_deleted, sort_order)
);
```

### menu_items 테이블 (수정)
```sql
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
    has_options BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store_category_active (store_id, category_id, is_deleted),
    INDEX idx_store_deleted (store_id, is_deleted),
    CONSTRAINT chk_price CHECK (price >= 0)
);
```

> `has_options` 필드: 옵션 그룹 생성/삭제 시 자동 갱신 (트리거 또는 서비스 레이어)

---

## 다음 단계

1. **개발자A와 세션 검증 API 합의** (우선)
2. DB 마이그레이션 스크립트 작성
3. Menu Service 구현 시작 (독립 개발 가능)
4. Order Service 구현 (Menu Service + Store Service API 계약 확정 후)
