# NFR Requirements — Frontend (Unit 5)

## 개요
프론트엔드 유닛의 비기능 요구사항 정의입니다.
Security Baseline 및 Property-Based Testing 확장 규칙을 준수합니다.

---

## 1. 성능 요구사항 (Performance)

### PERF-FE-01: 초기 로드 성능
- **번들 크기**: 초기 로드 500KB 이하 (gzip 기준)
- **코드 스플리팅**: 주요 페이지별 lazy loading 적용
  - Customer App: MenuPage, CartPage, OrderHistoryPage 분리
  - Admin App: OrderDashboard, TableManagement, MenuManagement 분리
- **First Contentful Paint (FCP)**: 2초 이내
- **Time to Interactive (TTI)**: 3초 이내

### PERF-FE-02: 런타임 성능
- **메뉴 목록 렌더링**: 100개 메뉴 항목 스크롤 시 60fps 유지
- **장바구니 업데이트**: 수량 변경 시 100ms 이내 UI 반영
- **SSE 이벤트 처리**: 수신 후 500ms 이내 UI 업데이트
- **페이지 전환**: 300ms 이내 (React Router)

### PERF-FE-03: 네트워크 최적화
- **이미지 최적화**: lazy loading, 적절한 크기 (메뉴 카드: 300x200px)
- **API 캐싱**: TanStack Query staleTime 설정 (메뉴: 5분, 주문: 30초)
- **중복 요청 방지**: TanStack Query 자동 deduplication 활용

---

## 2. 보안 요구사항 (Security) — Security Baseline 준수

### SEC-FE-01: XSS 방지 (SECURITY-05 준수)
- React의 기본 이스케이핑 활용 (JSX 자동 이스케이핑)
- `dangerouslySetInnerHTML` 사용 금지
- 사용자 입력 표시 시 추가 sanitization (DOMPurify 불필요 — React 기본 보호)
- URL 파라미터 검증 후 사용

### SEC-FE-02: 토큰 보안 저장 (SECURITY-12 준수)
- JWT 토큰: localStorage 저장 (httpOnly cookie 불가 — SPA 특성)
- **보완 조치**:
  - 토큰 만료 시간 엄격 체크
  - 탭 간 토큰 동기화 (storage event 리스닝)
  - 로그아웃 시 즉시 토큰 삭제
  - XSS 방지로 토큰 탈취 위험 최소화

### SEC-FE-03: CSP 정책 (SECURITY-04 준수)
- Content-Security-Policy 헤더 설정 (API Gateway/서버에서):
  ```
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';  // MUI 인라인 스타일 필요
  img-src 'self' https://*.s3.amazonaws.com;
  connect-src 'self' https://api.{domain};
  font-src 'self';
  ```
- `unsafe-eval` 사용 금지
- 외부 CDN 스크립트 사용 시 SRI (Subresource Integrity) 적용 (SECURITY-13)

### SEC-FE-04: HTTP 보안 헤더 (SECURITY-04 준수)
- Strict-Transport-Security: max-age=31536000; includeSubDomains
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin
- (서버/API Gateway에서 설정, 프론트엔드는 HTTPS 강제)

### SEC-FE-05: 입력 검증 (SECURITY-05 준수)
- 모든 폼 입력: Zod 스키마 기반 클라이언트 검증
- 서버 검증과 별개로 클라이언트 사전 검증 (UX 향상)
- 파일 업로드: 타입/크기 클라이언트 사전 체크

### SEC-FE-06: CORS 및 API 통신 (SECURITY-08 준수)
- API 요청 시 항상 Authorization 헤더 포함
- CORS: 서버에서 특정 origin만 허용 (wildcard 금지)
- 401 응답 시 즉시 로그아웃 처리

### SEC-FE-07: 에러 정보 노출 방지 (SECURITY-09 준수)
- 프로덕션 빌드: 소스맵 비공개 (서버 전송용만 생성)
- 에러 메시지: 사용자에게 기술적 상세 노출 금지
- 콘솔 로그: 프로덕션에서 debug/verbose 레벨 비활성화

### SEC-FE-08: 의존성 보안 (SECURITY-10 준수)
- pnpm-lock.yaml 커밋 (의존성 고정)
- `pnpm audit` CI 파이프라인에 포함
- 미사용 의존성 정기 제거
- 공식 npm registry만 사용

---

## 3. 테스트 요구사항 (Testing) — PBT 확장 준수

### TEST-FE-01: 테스트 커버리지 목표
- **전체 커버리지**: 60% 이상
- **비즈니스 로직**: 90% 이상 (장바구니, 인증, 금액 계산)
- **핵심 컴포넌트**: 70% 이상 (MenuPage, CartPage, OrderDashboard)

### TEST-FE-02: 단위 테스트 범위
- 비즈니스 로직 함수 (calculateItemTotal, calculateCartTotal 등)
- Reducer 함수 (cartReducer, authReducer)
- 유틸리티 함수 (formatPrice, formatDate, isTokenExpired)
- 커스텀 훅 (useAuth, useLocalStorage, useCart)

### TEST-FE-03: Property-Based Testing (PBT-01 ~ PBT-10 준수)
- **프레임워크**: fast-check (PBT-09)
- **PBT 대상 식별** (PBT-01):

| 컴포넌트 | 속성 카테고리 | 테스트할 속성 |
|----------|--------------|--------------|
| 장바구니 금액 계산 | Invariant (PBT-03) | totalAmount = sum(items.itemTotal), itemTotal = (price + optionsSum) × qty |
| 장바구니 상태 머신 | Stateful (PBT-06) | 어떤 순서로 add/remove/update해도 totalAmount >= 0, itemCount >= 0 |
| 가격 포맷 | Round-trip (PBT-02) | formatPrice(parsePrice(x)) preserves value |
| 옵션 선택 검증 | Invariant (PBT-03) | selectedCount always within [minSelections, maxSelections] |
| 수량 조절 | Invariant (PBT-03) | quantity always within [1, 99] |

- **Generator 품질** (PBT-07): 도메인 타입별 커스텀 generator 작성
  - `arbitraryMenuItem`: 유효한 메뉴 항목 생성 (price: 100~1000000)
  - `arbitraryCartItem`: 유효한 장바구니 항목 생성
  - `arbitraryOptionGroup`: 유효한 옵션 그룹 생성
- **Shrinking/재현성** (PBT-08): fast-check 기본 shrinking 활용, seed 로깅
- **보완 전략** (PBT-10): 핵심 시나리오는 example-based 테스트도 병행

### TEST-FE-04: 통합 테스트
- 주문 플로우 (메뉴 선택 → 옵션 → 장바구니 → 주문 확정)
- 로그인 플로우 (입력 → API 호출 → 토큰 저장 → 리다이렉트)
- SSE 연결 및 이벤트 처리 (Admin 대시보드)

---

## 4. 가용성 및 에러 복구 (Availability)

### AVAIL-FE-01: 에러 바운더리
- React Error Boundary 적용 (페이지 레벨)
- 에러 발생 시 fallback UI 표시 ("문제가 발생했습니다. 새로고침해주세요")
- 에러 정보 서버 전송 (에러 리포팅 API)

### AVAIL-FE-02: 네트워크 에러 대응
- API 호출 실패 시 TanStack Query 자동 재시도 (3회, 지수 백오프)
- 네트워크 끊김 감지 → 사용자 알림 (Toast)
- SSE 연결 끊김 → 자동 재연결 (3초 간격, 최대 5회)

### AVAIL-FE-03: 오프라인 대응
- 장바구니: localStorage에 저장되어 오프라인에서도 조회 가능
- 주문 생성: 오프라인 시 에러 메시지 + 재시도 안내
- 서비스 워커: MVP에서는 미적용 (향후 확장)

### AVAIL-FE-04: 에러 로깅 (SECURITY-03 준수)
- 구조화된 에러 로그: timestamp, errorType, message, componentStack, url
- 서버 전송: POST /errors (비동기, 실패해도 앱 동작에 영향 없음)
- 민감 정보 제외: 토큰, 비밀번호 등 로그에 포함 금지
- 프로덕션: console.error만 유지, debug/log 레벨 제거

---

## 5. 유지보수성 (Maintainability)

### MAINT-FE-01: 코드 품질 도구
- **ESLint**: @typescript-eslint + react-hooks 규칙
- **Prettier**: 코드 포맷 통일
- **Husky + lint-staged**: 커밋 전 자동 lint/format

### MAINT-FE-02: 타입 안전성
- TypeScript strict mode 활성화
- API 응답 타입: Zod 스키마로 런타임 검증
- `any` 타입 사용 금지 (eslint 규칙)

### MAINT-FE-03: 코드 구조
- 기능별 폴더 구조 (pages/, components/, hooks/, api/, contexts/)
- 컴포넌트당 1파일 원칙
- 공통 로직은 Shared 패키지로 추출

---

## 6. 사용성 (Usability)

### USAB-FE-01: 반응형 디자인
- Customer App: 태블릿 (768px+) 최적화, 모바일 (320px+) 지원
- Admin App: 데스크톱 (1024px+) 최적화, 태블릿 (768px+) 지원
- MUI 반응형 유틸리티 활용 (useMediaQuery, Grid)

### USAB-FE-02: 접근성 (WCAG 2.1 AA)
- 색상 대비 4.5:1 이상
- 모든 이미지 alt 텍스트
- 키보드 네비게이션 지원
- aria-label 적용 (아이콘 버튼)
- 포커스 관리 (모달 열림/닫힘)

### USAB-FE-03: 국제화 준비
- MVP에서는 한국어 단일 언어
- 텍스트 하드코딩 허용 (향후 i18n 라이브러리 도입 시 추출 용이하도록 컴포넌트 분리)

---

## Security Baseline Compliance Summary

| Rule | Status | 적용 내용 |
|------|--------|-----------|
| SECURITY-01 | N/A | 프론트엔드는 데이터 저장소 없음 (백엔드 담당) |
| SECURITY-02 | N/A | 네트워크 중간자 없음 (백엔드/인프라 담당) |
| SECURITY-03 | Compliant | AVAIL-FE-04에서 구조화된 에러 로깅 정의 |
| SECURITY-04 | Compliant | SEC-FE-03, SEC-FE-04에서 CSP/보안 헤더 정의 |
| SECURITY-05 | Compliant | SEC-FE-01, SEC-FE-05에서 입력 검증 정의 |
| SECURITY-06 | N/A | IAM 정책 없음 (인프라 담당) |
| SECURITY-07 | N/A | 네트워크 설정 없음 (인프라 담당) |
| SECURITY-08 | Compliant | SEC-FE-06에서 인증/인가 처리 정의 |
| SECURITY-09 | Compliant | SEC-FE-07에서 에러 정보 노출 방지 정의 |
| SECURITY-10 | Compliant | SEC-FE-08에서 의존성 보안 정의 |
| SECURITY-11 | Compliant | 인증 로직 AuthProvider로 격리, Rate limit은 서버 담당 |
| SECURITY-12 | Compliant | SEC-FE-02에서 토큰 관리 정의 |
| SECURITY-13 | Compliant | SEC-FE-03에서 SRI 적용 명시 |
| SECURITY-14 | N/A | 알림/모니터링은 인프라 담당 (프론트엔드는 에러 전송만) |
| SECURITY-15 | Compliant | AVAIL-FE-01에서 Error Boundary, 에러 처리 정의 |

## PBT Compliance Summary

| Rule | Status | 적용 내용 |
|------|--------|-----------|
| PBT-01 | Compliant | TEST-FE-03에서 속성 식별 완료 (5개 속성) |
| PBT-02 | Compliant | 가격 포맷 round-trip 테스트 계획 |
| PBT-03 | Compliant | 장바구니 금액, 옵션 선택, 수량 invariant 계획 |
| PBT-04 | N/A | 프론트엔드에 idempotent 연산 해당 없음 |
| PBT-05 | N/A | Oracle/참조 구현 해당 없음 |
| PBT-06 | Compliant | 장바구니 상태 머신 stateful PBT 계획 |
| PBT-07 | Compliant | 도메인 타입별 커스텀 generator 계획 |
| PBT-08 | Compliant | fast-check 기본 shrinking + seed 로깅 |
| PBT-09 | Compliant | fast-check 선택 및 문서화 |
| PBT-10 | Compliant | example-based + PBT 병행 전략 |
