# Unit of Work 의존성

## 의존성 매트릭스

| Unit (행 → 열에 의존) | Auth | Store | Menu | Order | Frontend |
|------------------------|------|-------|------|-------|----------|
| **Unit 1: Auth** | - | - | - | - | - |
| **Unit 2: Store** | - | - | - | ✅ | - |
| **Unit 3: Menu** | - | - | - | - | - |
| **Unit 4: Order** | - | - | ✅ | - | - |
| **Unit 5: Frontend** | ✅ | ✅ | ✅ | ✅ | - |

---

## 개발 순서 (병렬 개발)

### Phase 1: API 계약 정의 (모든 유닛 공통)
모든 백엔드 서비스의 API 스펙(OpenAPI)을 먼저 정의하여 병렬 개발 가능하게 함.

### Phase 2: 병렬 구현

```
+------------------------------------------+
|          병렬 개발 가능 그룹               |
+------------------------------------------+
|                                          |
|  Unit 1: Auth    (독립)                  |
|  Unit 3: Menu    (독립)                  |
|  Unit 2: Store   (Order API 계약만 필요)  |
|  Unit 4: Order   (Menu API 계약만 필요)   |
|                                          |
+------------------------------------------+
              |
              v (백엔드 API 완성 후)
+------------------------------------------+
|          프론트엔드 개발                   |
+------------------------------------------+
|                                          |
|  Unit 5: Frontend (통합)                 |
|    - Shared UI                           |
|    - Customer App                        |
|    - Admin App                           |
|                                          |
+------------------------------------------+
```

### 병렬화 분석

| 유닛 | 병렬 개발 가능 | 조건 |
|------|----------------|------|
| Unit 1: Auth | ✅ 완전 독립 | 없음 |
| Unit 2: Store | ✅ 조건부 | Order Service API 계약 정의 필요 |
| Unit 3: Menu | ✅ 완전 독립 | 없음 |
| Unit 4: Order | ✅ 조건부 | Menu Service API 계약 정의 필요 |
| Unit 5: Frontend | ⚠️ 백엔드 후 | 모든 백엔드 API 필요 (Mock 가능) |

---

## 통합 포인트

### 서비스 간 HTTP 통신
| 호출자 | 대상 | 엔드포인트 | 목적 |
|--------|------|-----------|------|
| Store Service | Order Service | POST /internal/orders/archive | 세션 종료 시 주문 아카이브 |
| Order Service | Menu Service | GET /internal/menus/{id}/validate | 주문 시 가격 검증 |

### 프론트엔드 → API Gateway
| 프론트엔드 앱 | 대상 서비스 | 주요 API |
|--------------|------------|---------|
| Customer App | Auth, Menu, Order | 로그인, 메뉴 조회, 주문 생성/조회 |
| Admin App | Auth, Store, Menu, Order | 로그인, 테이블/메뉴 관리, 주문 모니터링 |

### SSE 연결
| 구독자 | 발행자 | 이벤트 |
|--------|--------|--------|
| Admin App | Order Service | new_order, status_changed, order_deleted |
| Customer App (선택) | Order Service | status_changed |

---

## 통합 테스트 전략

| 통합 시점 | 테스트 범위 |
|-----------|------------|
| Unit 2 + Unit 4 완료 후 | Store → Order 아카이브 연동 |
| Unit 3 + Unit 4 완료 후 | Order → Menu 가격 검증 연동 |
| 모든 백엔드 완료 후 | 전체 API 통합 테스트 |
| Unit 5 완료 후 | E2E 시나리오 테스트 |
