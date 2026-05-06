# Functional Design Plan — Menu Service + Order Service (개발자 B)

## 개요
Unit 3 (Menu Service)과 Unit 4 (Order Service)의 상세 비즈니스 로직 설계 계획입니다.

---

## 담당 범위 요약

| 유닛 | 서비스 | 핵심 도메인 |
|------|--------|-------------|
| Unit 3 | Menu Service | 카테고리, 메뉴 항목, 옵션 그룹/항목, S3 이미지 |
| Unit 4 | Order Service | 주문 생성/조회/상태관리/삭제/이력, SSE 실시간 스트림 |

### 서비스 간 연동 관계
- **Order Service → Menu Service**: 주문 생성 시 메뉴/옵션 가격 검증 (HTTP 내부 API)
- **Store Service → Order Service**: 테이블 세션 종료 시 주문 아카이브 요청 수신

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
메뉴 항목의 가격 검증 범위는 어떻게 하시겠습니까?

A) 가격은 0원 이상만 허용 (무료 메뉴 가능)
B) 가격은 100원 이상만 허용 (최소 가격 제한)
C) 가격은 0원 이상, 상한선 1,000,000원 이하
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
메뉴 삭제 시 해당 메뉴가 포함된 기존 주문 처리는 어떻게 하시겠습니까?

A) 소프트 삭제 (is_deleted 플래그) — 기존 주문에서 메뉴명/가격 조회 가능
B) 하드 삭제 — 기존 주문에는 주문 시점의 메뉴명/가격이 스냅샷으로 저장되어 있으므로 무관
C) 활성 주문(대기중/준비중)이 있는 메뉴는 삭제 불가 (완료 후에만 삭제 가능)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
주문 생성 시 가격 검증 실패(메뉴 가격 변경 등) 처리는 어떻게 하시겠습니까?

A) 주문 거부 + 클라이언트에 최신 가격 정보 반환 (재주문 유도)
B) 서버 측 최신 가격으로 자동 보정 후 주문 생성 (클라이언트에 보정된 금액 알림)
C) 주문 거부만 수행 (클라이언트가 메뉴를 다시 조회해야 함)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 4
주문 상태 전이 규칙은 어떻게 하시겠습니까?

A) 단방향만 허용: 대기중 → 준비중 → 완료 (되돌리기 불가)
B) 제한적 되돌리기 허용: 준비중 → 대기중 가능, 완료 → 되돌리기 불가
C) 자유 전이: 어떤 상태에서든 다른 상태로 변경 가능
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 5
SSE 연결 관리 전략은 어떻게 하시겠습니까?

A) 매장(store_id)별 단일 SSE 스트림 (모든 테이블 주문 이벤트 통합)
B) 매장별 + 테이블별 분리 SSE 스트림 (관리자는 매장 전체, 고객은 자기 테이블만)
C) 매장별 단일 스트림 + 클라이언트 측 필터링 (고객 앱에서 자기 테이블만 표시)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 6
주문 이력 아카이브 시 데이터 이동 방식은 어떻게 하시겠습니까?

A) 원본 주문 데이터를 order_history 테이블로 복사 후 원본 삭제
B) 원본 주문에 archived_at 타임스탬프 추가 (같은 테이블에 유지, 조회 시 필터)
C) 원본 주문 데이터를 order_history 테이블로 이동 (INSERT + DELETE 트랜잭션)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 7
옵션 그룹의 선택 규칙은 어떻게 하시겠습니까?

A) 필수 선택 그룹 (min_select=1) + 선택 선택 그룹 (min_select=0), 최대 선택 수 제한
B) 모든 옵션 그룹은 선택 사항 (min_select=0), 최대 선택 수만 제한
C) 단일 선택 그룹 (라디오) + 다중 선택 그룹 (체크박스) 타입 분리
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## 실행 단계

### Menu Service (Unit 3)

- [ ] Step 1: Menu Service 도메인 엔티티 설계
  - [ ] Category 엔티티 (카테고리)
  - [ ] MenuItem 엔티티 (메뉴 항목)
  - [ ] OptionGroup 엔티티 (옵션 그룹)
  - [ ] OptionItem 엔티티 (옵션 항목)

- [ ] Step 2: Menu Service 비즈니스 규칙 정의
  - [ ] 카테고리 CRUD 규칙
  - [ ] 메뉴 항목 CRUD 규칙 (가격 검증 포함)
  - [ ] 옵션 그룹/항목 관리 규칙
  - [ ] 메뉴 노출 순서 관리 규칙
  - [ ] 메뉴 삭제 시 cascade 규칙

- [ ] Step 3: Menu Service 외부 연동 설계
  - [ ] S3 Presigned URL 발급 로직
  - [ ] 내부 API: 가격 검증 엔드포인트 (Order Service용)

- [ ] Step 4: Menu Service DB 스키마 설계
  - [ ] categories 테이블
  - [ ] menu_items 테이블
  - [ ] option_groups 테이블
  - [ ] option_items 테이블

### Order Service (Unit 4)

- [ ] Step 5: Order Service 도메인 엔티티 설계
  - [ ] Order 엔티티 (주문)
  - [ ] OrderItem 엔티티 (주문 항목)
  - [ ] OrderItemOption 엔티티 (주문 항목 옵션)
  - [ ] OrderHistory 엔티티 (주문 이력)

- [ ] Step 6: Order Service 비즈니스 규칙 정의
  - [ ] 주문 생성 규칙 (가격 검증 포함)
  - [ ] 주문 상태 전이 규칙 (상태 머신)
  - [ ] 주문 삭제 규칙 (관리자 전용)
  - [ ] 주문 이력 아카이브 규칙
  - [ ] 주문 금액 계산 규칙

- [ ] Step 7: Order Service SSE 설계
  - [ ] SSE 이벤트 타입 정의 (new_order, status_changed, order_deleted)
  - [ ] 연결 관리 전략 (매장별 스트림)
  - [ ] 재연결 처리

- [ ] Step 8: Order Service 외부 연동 설계
  - [ ] Menu Service 가격 검증 호출 (HTTP)
  - [ ] Store Service로부터 아카이브 요청 수신 (내부 API)

- [ ] Step 9: Order Service DB 스키마 설계
  - [ ] orders 테이블
  - [ ] order_items 테이블
  - [ ] order_item_options 테이블
  - [ ] order_history 테이블

### 통합

- [ ] Step 10: 비즈니스 로직 모델 통합
  - [ ] Menu ↔ Order 가격 검증 연동 로직
  - [ ] Store → Order 아카이브 연동 로직
  - [ ] 에러 시나리오 정의 (서비스 간 통신 실패 등)

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| 프레임워크 | FastAPI (Python) |
| 데이터베이스 | MySQL (RDS), 서비스별 스키마 분리 |
| 데이터 접근 | Raw SQL + 데이터 매퍼 패턴 |
| 이미지 저장 | AWS S3 (Presigned URL) |
| 실시간 통신 | SSE (Server-Sent Events) |
| 테스트 | 단위 테스트 + PBT (Property-Based Testing) |
| API 문서 | Swagger (OpenAPI) |

---

## 코드 조직

### Menu Service
```
services/menu-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── queries/
│   │   └── mappers/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── external/
│       └── s3_client.py
├── tests/
├── migrations/
├── requirements.txt
└── Dockerfile
```

### Order Service
```
services/order-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── queries/
│   │   └── mappers/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── sse/
│       └── event_manager.py
├── tests/
├── migrations/
├── requirements.txt
└── Dockerfile
```

---

## API 엔드포인트 목록

### Menu Service API

| Method | Path | Purpose | 권한 |
|--------|------|---------|------|
| GET | /stores/{store_id}/categories | 카테고리 목록 조회 | 고객/관리자 |
| POST | /stores/{store_id}/categories | 카테고리 생성 | 관리자 |
| PUT | /categories/{category_id} | 카테고리 수정 | 관리자 |
| DELETE | /categories/{category_id} | 카테고리 삭제 | 관리자 |
| GET | /stores/{store_id}/menus | 메뉴 목록 조회 | 고객/관리자 |
| POST | /stores/{store_id}/menus | 메뉴 등록 | 관리자 |
| PUT | /menus/{menu_id} | 메뉴 수정 | 관리자 |
| DELETE | /menus/{menu_id} | 메뉴 삭제 | 관리자 |
| POST | /menus/{menu_id}/image | 이미지 업로드 URL 발급 | 관리자 |
| GET | /menus/{menu_id}/options | 옵션 그룹 조회 | 고객/관리자 |
| POST | /menus/{menu_id}/options | 옵션 그룹 생성 | 관리자 |
| PUT | /option-groups/{group_id} | 옵션 그룹 수정 | 관리자 |
| DELETE | /option-groups/{group_id} | 옵션 그룹 삭제 | 관리자 |
| GET | /internal/menus/{menu_id}/validate | 가격 검증 (내부 API) | Order Service |

### Order Service API

| Method | Path | Purpose | 권한 |
|--------|------|---------|------|
| POST | /stores/{store_id}/orders | 주문 생성 | 고객 |
| GET | /stores/{store_id}/orders | 주문 목록 (매장 전체) | 관리자 |
| GET | /stores/{store_id}/tables/{table_id}/orders | 테이블 주문 조회 | 고객/관리자 |
| PATCH | /orders/{order_id}/status | 주문 상태 변경 | 관리자 |
| DELETE | /orders/{order_id} | 주문 삭제 | 관리자 |
| GET | /stores/{store_id}/tables/{table_id}/history | 과거 주문 이력 | 관리자 |
| GET | /stores/{store_id}/orders/stream | SSE 실시간 주문 스트림 | 관리자 |
| POST | /internal/orders/archive | 세션 주문 아카이브 (내부 API) | Store Service |

---

## 완료 기준

### Menu Service
- [ ] 카테고리 CRUD API 구현 및 테스트
- [ ] 메뉴 항목 CRUD API 구현 및 테스트
- [ ] 옵션 그룹/항목 CRUD API 구현 및 테스트
- [ ] 이미지 업로드 URL 발급 API 구현
- [ ] 메뉴 순서 조정 API 구현
- [ ] 내부 가격 검증 API 구현
- [ ] 단위 테스트 + PBT (가격 검증 invariant)
- [ ] Swagger 문서 완성

### Order Service
- [ ] 주문 생성 API 구현 (Menu Service 가격 검증 연동)
- [ ] 주문 조회 API 구현 (테이블별, 매장별)
- [ ] 주문 상태 변경 API 구현
- [ ] 주문 삭제 API 구현
- [ ] 주문 이력 아카이브 API 구현
- [ ] SSE 실시간 스트림 엔드포인트 구현
- [ ] 내부 아카이브 API 구현 (Store Service용)
- [ ] 단위 테스트 + PBT (주문 금액 계산 invariant, 상태 머신)
- [ ] Swagger 문서 완성

---

## PBT (Property-Based Testing) 대상 속성

### Menu Service
1. **가격 invariant**: 모든 메뉴 가격은 허용 범위 내여야 한다
2. **정렬 invariant**: sort_order 변경 후에도 모든 항목의 순서가 유일해야 한다
3. **cascade 삭제**: 메뉴 삭제 시 관련 옵션 그룹/항목이 모두 삭제되어야 한다

### Order Service
1. **금액 계산 invariant**: 주문 총액 = Σ(각 항목 단가 × 수량 + 선택 옵션 가격 × 수량)
2. **상태 머신 invariant**: 주문 상태는 정의된 전이 규칙만 따라야 한다
3. **아카이브 무결성**: 아카이브 후 원본 주문은 조회되지 않고, 이력에서만 조회되어야 한다

---

## 참고 문서
- [전체 요구사항](../../requirements/table-order-requirements.md)
- [컴포넌트 정의](../inception/application-design/components.md)
- [메서드 시그니처](../inception/application-design/component-methods.md)
- [서비스 레이어 설계](../inception/application-design/services.md)
- [의존성 매핑](../inception/application-design/component-dependency.md)
- [Unit of Work 정의](../inception/application-design/unit-of-work.md)
