# Unit of Work — Story Map

## 스토리-유닛 매핑

| 스토리 | 주 담당 유닛 | 보조 유닛 | 설명 |
|--------|-------------|-----------|------|
| US-01: 테이블 자동 로그인 | Unit 1 (Auth) + Unit 5 (Frontend) | Unit 2 (Store) | Auth: 인증 API, Frontend: 자동 로그인 UI, Store: 테이블 정보 |
| US-02: 메뉴 조회 및 탐색 | Unit 3 (Menu) + Unit 5 (Frontend) | - | Menu: 조회 API, Frontend: 메뉴 UI |
| US-03: 메뉴 옵션 선택 | Unit 3 (Menu) + Unit 5 (Frontend) | - | Menu: 옵션 API, Frontend: 옵션 선택 UI |
| US-04: 장바구니 관리 | Unit 5 (Frontend) | - | 순수 프론트엔드 (로컬 저장) |
| US-05: 주문 생성 | Unit 4 (Order) + Unit 5 (Frontend) | Unit 3 (Menu) | Order: 생성 API, Frontend: 주문 UI, Menu: 가격 검증 |
| US-06: 주문 내역 조회 | Unit 4 (Order) + Unit 5 (Frontend) | - | Order: 조회 API, Frontend: 내역 UI |
| US-07: 매장 관리자 인증 | Unit 1 (Auth) + Unit 5 (Frontend) | - | Auth: 관리자 인증 API, Frontend: 로그인 UI |
| US-08: 실시간 주문 모니터링 | Unit 4 (Order) + Unit 5 (Frontend) | - | Order: SSE 스트림, Frontend: 대시보드 UI |
| US-09: 테이블 관리 | Unit 2 (Store) + Unit 5 (Frontend) | Unit 4 (Order) | Store: 테이블/세션 API, Frontend: 관리 UI, Order: 아카이브 |
| US-10: 메뉴 관리 | Unit 3 (Menu) + Unit 5 (Frontend) | - | Menu: CRUD API, Frontend: 메뉴 관리 UI |

---

## 유닛별 스토리 할당 요약

### Unit 1: Auth Service
| 스토리 | 역할 |
|--------|------|
| US-01 | 테이블 태블릿 인증 API |
| US-07 | 관리자 로그인 API |

### Unit 2: Store Service
| 스토리 | 역할 |
|--------|------|
| US-01 | 테이블 정보 제공 (보조) |
| US-09 | 테이블 관리, 세션 라이프사이클 |

### Unit 3: Menu Service
| 스토리 | 역할 |
|--------|------|
| US-02 | 메뉴 조회 API |
| US-03 | 옵션 그룹/항목 조회 API |
| US-05 | 가격 검증 (보조) |
| US-10 | 메뉴 CRUD, 옵션 관리 API |

### Unit 4: Order Service
| 스토리 | 역할 |
|--------|------|
| US-05 | 주문 생성 API |
| US-06 | 주문 내역 조회 API |
| US-08 | SSE 실시간 스트림, 상태 관리 |
| US-09 | 주문 아카이브 (보조) |

### Unit 5: Frontend (통합)
| 스토리 | 역할 |
|--------|------|
| US-01 | 자동 로그인 UI (Customer App) |
| US-02 | 메뉴 조회 UI (Customer App) |
| US-03 | 옵션 선택 UI (Customer App) |
| US-04 | 장바구니 관리 — 전체 (Customer App) |
| US-05 | 주문 생성 UI (Customer App) |
| US-06 | 주문 내역 UI (Customer App) |
| US-07 | 로그인 UI (Admin App) |
| US-08 | 주문 대시보드 UI — SSE (Admin App) |
| US-09 | 테이블 관리 UI (Admin App) |
| US-10 | 메뉴 관리 UI (Admin App) |

---

## 크로스-유닛 스토리 분할 전략

### US-01 (테이블 자동 로그인) — 3개 유닛 관여
- **Unit 1 (Auth)**: 테이블 인증 엔드포인트 구현
- **Unit 2 (Store)**: 테이블 정보 조회 엔드포인트
- **Unit 5 (Frontend)**: 자동 로그인 로직, 토큰 로컬 저장

### US-05 (주문 생성) — 3개 유닛 관여
- **Unit 3 (Menu)**: 내부 가격 검증 엔드포인트
- **Unit 4 (Order)**: 주문 생성 로직, Menu Service 호출
- **Unit 5 (Frontend)**: 주문 확인 UI, API 호출

### US-09 (테이블 관리) — 3개 유닛 관여
- **Unit 2 (Store)**: 세션 종료 로직, Order Service 호출
- **Unit 4 (Order)**: 주문 아카이브 내부 엔드포인트
- **Unit 5 (Frontend)**: 테이블 관리 UI

---

## 매핑 완전성 검증

| 검증 항목 | 결과 |
|-----------|------|
| 모든 스토리(US-01~US-10) 할당됨 | ✅ |
| 모든 유닛에 최소 1개 스토리 할당 | ✅ |
| 크로스-유닛 스토리 분할 전략 정의됨 | ✅ |
| 고아 스토리 없음 | ✅ |
