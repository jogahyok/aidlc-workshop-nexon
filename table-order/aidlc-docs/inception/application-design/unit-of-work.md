# Unit of Work 정의

## 개발 전략
- **개발 방식**: 병렬 개발 (API 계약 먼저 정의 후 동시 개발)
- **프론트엔드 분리**: 1개 유닛으로 통합 (Customer App + Admin App + Shared UI)
- **인프라 처리**: 각 서비스 유닛에 자체 인프라 포함
- **완료 기준**: API 구현 + 테스트 (단위+PBT) + API 문서 (Swagger)
- **팀 구성**: 3명 개발자 병렬 작업

## 개발자 배분

| 개발자 | 담당 유닛 | 도메인 |
|--------|-----------|--------|
| **개발자 A** | Unit 1 (Auth) + Unit 2 (Store) | 인증/세션/매장/테이블 관리 |
| **개발자 B** | Unit 3 (Menu) + Unit 4 (Order) | 메뉴/옵션/주문/실시간 |
| **개발자 C** | Unit 5 (Frontend) | 전체 프론트엔드 UI |

### 배분 근거
- **개발자 A**: Auth↔Store 세션 연관성, 보안 로직 집중
- **개발자 B**: Menu↔Order 가격 검증 내부 API 연동, 핵심 비즈니스 로직
- **개발자 C**: UI 일관성 유지, Shared UI 공통 패턴 적용

---

## Unit 1: Auth Service

### 범위 및 책임
- 관리자 로그인/로그아웃
- 테이블 태블릿 인증
- JWT 토큰 발급/검증/갱신
- 로그인 시도 제한 (brute-force 방지)

### 포함 컴포넌트
- Auth Service (FastAPI)
- DB 스키마: admins, table_credentials, login_attempts

### 코드 조직
```
services/auth-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── queries/
│   │   └── mappers/
│   ├── models/
│   ├── schemas/
│   └── services/
├── tests/
├── migrations/
├── requirements.txt
└── Dockerfile
```

### 완료 기준
- [ ] 관리자 로그인 API (POST /auth/admin/login)
- [ ] 테이블 로그인 API (POST /auth/table/login)
- [ ] 토큰 검증 API (GET /auth/me)
- [ ] 로그인 시도 제한 구현
- [ ] 단위 테스트 + PBT (JWT 토큰 round-trip)
- [ ] Swagger 문서 완성

---

## Unit 2: Store Service

### 범위 및 책임
- 매장 정보 관리
- 테이블 CRUD
- 테이블 세션 라이프사이클 (시작/종료)
- 테이블 이용 완료 처리

### 포함 컴포넌트
- Store Service (FastAPI)
- DB 스키마: stores, tables, table_sessions

### 코드 조직
```
services/store-service/
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
│   └── services/
├── tests/
├── migrations/
├── requirements.txt
└── Dockerfile
```

### 완료 기준
- [ ] 매장 정보 조회 API
- [ ] 테이블 CRUD API
- [ ] 테이블 세션 관리 API (시작/종료)
- [ ] 이용 완료 시 Order Service 연동 (HTTP)
- [ ] 단위 테스트 + PBT (세션 상태 머신)
- [ ] Swagger 문서 완성

---

## Unit 3: Menu Service

### 범위 및 책임
- 카테고리 CRUD
- 메뉴 항목 CRUD
- 옵션 그룹/항목 CRUD
- 메뉴 이미지 업로드 (S3 Presigned URL)
- 메뉴 노출 순서 관리

### 포함 컴포넌트
- Menu Service (FastAPI)
- DB 스키마: categories, menu_items, option_groups, option_items
- S3 연동 (이미지 업로드)

### 코드 조직
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

### 완료 기준
- [ ] 카테고리 CRUD API
- [ ] 메뉴 항목 CRUD API
- [ ] 옵션 그룹/항목 CRUD API
- [ ] 이미지 업로드 URL 발급 API
- [ ] 메뉴 순서 조정 API
- [ ] 단위 테스트 + PBT (가격 검증 invariant)
- [ ] Swagger 문서 완성

---

## Unit 4: Order Service

### 범위 및 책임
- 주문 생성 (메뉴/옵션 가격 검증)
- 주문 상태 관리 (대기중 → 준비중 → 완료)
- 주문 조회 (테이블별, 매장별)
- 주문 삭제 (관리자)
- 주문 이력 아카이브
- SSE 실시간 주문 스트림

### 포함 컴포넌트
- Order Service (FastAPI)
- DB 스키마: orders, order_items, order_item_options, order_history
- SSE 엔드포인트
- Menu Service 연동 (가격 검증)

### 코드 조직
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

### 완료 기준
- [ ] 주문 생성 API (가격 검증 포함)
- [ ] 주문 조회 API (테이블별, 매장별)
- [ ] 주문 상태 변경 API
- [ ] 주문 삭제 API
- [ ] 주문 이력 아카이브 API
- [ ] SSE 실시간 스트림 엔드포인트
- [ ] 단위 테스트 + PBT (주문 금액 계산 invariant, 상태 머신)
- [ ] Swagger 문서 완성

---

## Unit 5: Frontend (모노레포 통합)

### 범위 및 책임
- 고객용 웹 인터페이스 (Customer App)
- 관리자용 웹 인터페이스 (Admin App)
- 공통 UI 라이브러리 (Shared UI)

### 포함 컴포넌트
- Customer App (React TypeScript) — 메뉴 조회, 옵션 선택, 장바구니, 주문
- Admin App (React TypeScript) — 로그인, 주문 대시보드, 테이블/메뉴 관리
- Shared UI Library — 공통 컴포넌트, 훅, 타입, 유틸리티

### 코드 조직
```
frontend/
├── packages/
│   ├── shared/              # 공통 컴포넌트, 훅, 타입, 유틸리티
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   └── package.json
│   ├── customer-app/        # 고객용 앱
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── contexts/
│   │   │   ├── hooks/
│   │   │   └── api/
│   │   └── package.json
│   └── admin-app/           # 관리자용 앱
│       ├── src/
│       │   ├── pages/
│       │   ├── components/
│       │   ├── contexts/
│       │   ├── hooks/
│       │   └── api/
│       └── package.json
├── package.json             # 모노레포 루트
└── tsconfig.json
```

### 완료 기준
- [ ] **Shared UI**: 공통 컴포넌트 (Button, Card, Modal, Loading, Toast, Input)
- [ ] **Customer App**: 자동 로그인, 메뉴 조회, 옵션 선택, 장바구니, 주문, 내역
- [ ] **Admin App**: 로그인, 주문 대시보드(SSE), 테이블 관리, 메뉴 관리
- [ ] 단위 테스트 + PBT (장바구니 금액 계산)
- [ ] 반응형 UI (태블릿 + 모바일)
