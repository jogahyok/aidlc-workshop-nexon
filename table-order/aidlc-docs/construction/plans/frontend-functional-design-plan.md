# Functional Design Plan — Frontend (개발자 C)

## 개요
Unit 5 (Frontend)의 상세 UI 컴포넌트 설계 및 프론트엔드 비즈니스 로직 설계 계획입니다.
모노레포 구조로 Customer App, Admin App, Shared UI 3개 패키지를 포함합니다.

**담당 스토리**: US-01 ~ US-10 (전체 10개 스토리의 프론트엔드 UI 부분)

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
UI 디자인 시스템/컴포넌트 라이브러리는 어떻게 하시겠습니까?

A) 완전 커스텀 디자인 시스템 (Tailwind CSS 기반, 모든 컴포넌트 직접 구현)
B) 기존 UI 라이브러리 사용 (MUI / Material UI)
C) 기존 UI 라이브러리 사용 (Ant Design)
D) 경량 Headless UI 라이브러리 (Radix UI + Tailwind CSS)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 2
Customer App의 라우팅 및 페이지 구조는 어떻게 하시겠습니까?

A) 단일 페이지 (SPA) — 탭/섹션으로 메뉴, 장바구니, 주문내역 전환
B) 멀티 페이지 라우팅 (React Router) — /menu, /cart, /orders 등 별도 페이지
C) 하이브리드 — 메뉴+옵션은 단일 페이지, 장바구니/주문은 별도 페이지
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 3
장바구니 로컬 저장 전략은 어떻게 하시겠습니까?

A) localStorage에 JSON 직렬화 (단순, 용량 제한 5MB)
B) IndexedDB 사용 (대용량 지원, 비동기 API)
C) localStorage + 만료 시간 관리 (세션 종료 시 자동 삭제)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 4
Admin App의 주문 대시보드 레이아웃은 어떻게 하시겠습니까?

A) 테이블 그리드 카드 레이아웃 (테이블별 카드, 클릭 시 상세 모달)
B) 칸반 보드 스타일 (대기중 | 준비중 | 완료 컬럼)
C) 리스트 뷰 + 필터 (주문 목록 테이블, 상태/테이블 필터)
D) 그리드 + 사이드 패널 (테이블 그리드 좌측, 선택 시 우측 패널에 상세)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 5
모노레포 빌드 도구는 무엇을 사용하시겠습니까?

A) Vite + pnpm workspaces (빠른 빌드, 모던 도구)
B) Create React App + yarn workspaces (안정적, 설정 간단)
C) Next.js + Turborepo (SSR 지원, 캐싱 최적화)
D) Vite + npm workspaces (Vite 빌드 + npm 기본 워크스페이스)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 6
API 통신 레이어는 어떻게 구성하시겠습니까?

A) Axios + 커스텀 훅 (useQuery 패턴 직접 구현)
B) TanStack Query (React Query) + Axios (캐싱, 자동 재시도, 상태 관리)
C) SWR + fetch API (경량, Vercel 생태계)
D) fetch API + 커스텀 훅 (외부 의존성 최소화)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 7
폼 관리 및 유효성 검증은 어떻게 하시겠습니까?

A) React Hook Form + Zod (타입 안전, 스키마 기반 검증)
B) Formik + Yup (성숙한 생태계, 풍부한 문서)
C) 커스텀 훅으로 직접 구현 (외부 의존성 최소화)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 8
Customer App에서 SSE(실시간 주문 상태 업데이트) 수신이 필요합니까?

A) 필요 없음 — 고객은 수동 새로고침 또는 폴링으로 상태 확인
B) 필요함 — 주문 상태 변경 시 실시간 알림 (Toast/배지)
C) 선택적 — 주문 내역 페이지에서만 자동 갱신 (폴링 30초 간격)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## 실행 단계

- [x] Step 1: Shared UI 컴포넌트 설계
  - [x] 공통 컴포넌트 목록 및 Props 정의
  - [x] 공통 훅 (useApi, useAuth, useLocalStorage) 인터페이스
  - [x] 공통 타입 정의 (Store, Table, MenuItem, Order 등)
  - [x] 유틸리티 함수 (formatPrice, formatDate, apiClient)

- [x] Step 2: Customer App 컴포넌트 설계
  - [x] 페이지 구조 및 라우팅 설계
  - [x] AuthProvider — 자동 로그인 로직
  - [x] MenuPage — 카테고리/메뉴 표시 로직
  - [x] MenuOptionModal — 옵션 선택 및 가격 계산
  - [x] CartProvider — 장바구니 상태 관리 (Context + useReducer)
  - [x] CartPage — 수량 조절, 삭제, 총액 계산
  - [x] OrderConfirmPage — 주문 확정 플로우
  - [x] OrderHistoryPage — 주문 내역 조회

- [x] Step 3: Admin App 컴포넌트 설계
  - [x] 페이지 구조 및 라우팅 설계
  - [x] AuthProvider — 관리자 로그인/로그아웃
  - [x] LoginPage — 로그인 폼 및 에러 처리
  - [x] OrderDashboard — SSE 연결, 테이블별 주문 현황
  - [x] OrderDetailModal — 주문 상세, 상태 변경
  - [x] TableManagement — 테이블 CRUD, 세션 관리
  - [x] MenuManagement — 메뉴/옵션 CRUD, 이미지 업로드
  - [x] OrderHistoryModal — 과거 주문 내역, 날짜 필터

- [x] Step 4: 프론트엔드 비즈니스 규칙 정의
  - [x] 장바구니 금액 계산 규칙 (옵션 가격 포함)
  - [x] 폼 유효성 검증 규칙
  - [x] 인증 상태 관리 규칙 (토큰 만료, 자동 갱신)
  - [x] 에러 처리 및 사용자 피드백 규칙

- [x] Step 5: 사용자 인터랙션 플로우 정의
  - [x] Customer App 주문 플로우 (메뉴 선택 → 옵션 → 장바구니 → 주문)
  - [x] Admin App 주문 처리 플로우 (수신 → 상태 변경 → 완료)
  - [x] Admin App 테이블 관리 플로우 (설정 → 운영 → 이용 완료)
  - [x] Admin App 메뉴 관리 플로우 (등록 → 수정 → 삭제)
