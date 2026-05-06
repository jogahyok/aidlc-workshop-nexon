# Frontend Components Design

## 개요
Customer App, Admin App, Shared UI의 컴포넌트 계층 구조, Props, 상태, API 연동 정의입니다.

---

## 1. Shared UI Library

### 공통 컴포넌트

| 컴포넌트 | Props | 설명 |
|----------|-------|------|
| Button | variant, size, disabled, loading, onClick | 기본 버튼 (MUI Button 래핑) |
| Card | title, children, onClick, highlighted | 카드 컨테이너 |
| Modal | open, onClose, title, children, actions | 모달 다이얼로그 |
| Loading | size, fullScreen | 로딩 스피너 |
| Toast | message, severity, duration | 알림 토스트 (MUI Snackbar) |
| Input | label, error, helperText, ...props | 텍스트 입력 (MUI TextField 래핑) |
| Select | label, options, value, onChange | 셀렉트 박스 |
| Badge | content, color, children | 배지 (상태 표시) |
| ConfirmDialog | open, title, message, onConfirm, onCancel | 확인 다이얼로그 |
| EmptyState | icon, title, description, action | 빈 상태 표시 |
| PriceDisplay | amount, size | 가격 표시 (₩ 포맷) |
| QuantityControl | value, min, max, onChange | 수량 조절 (+/-) |

### 공통 훅

| 훅 | 파라미터 | 반환값 | 설명 |
|----|----------|--------|------|
| useAuth | - | AuthState, login, logout | 인증 상태 관리 |
| useLocalStorage | key, initialValue | [value, setValue, remove] | localStorage 래퍼 |
| useApi | - | axiosInstance | 인증 헤더 포함 Axios 인스턴스 |
| useToast | - | showToast(message, severity) | Toast 알림 표시 |
| useConfirm | - | confirm(title, message): Promise<boolean> | 확인 다이얼로그 |

### 공통 유틸리티

```typescript
// 가격 포맷
formatPrice(amount: number): string  // → "₩12,000"

// 날짜 포맷
formatDate(isoString: string): string  // → "2026-05-06 14:30"
formatTime(isoString: string): string  // → "14:30"
formatRelativeTime(isoString: string): string  // → "3분 전"

// API 클라이언트 생성
createApiClient(baseUrl: string, token?: string): AxiosInstance
```

---

## 2. Customer App 컴포넌트

### 페이지 구조 (React Router)

```
/                    → 자동 로그인 처리 (AuthGuard)
/menu                → MenuPage (메뉴 조회)
/menu/:menuId        → MenuDetailPage (옵션 선택)
/cart                → CartPage (장바구니)
/cart/confirm        → OrderConfirmPage (주문 확인)
/orders              → OrderHistoryPage (주문 내역)
/error               → ErrorPage (인증 에러)
```

### 컴포넌트 계층

```
CustomerApp
├── AuthProvider
│   ├── AuthGuard (인증 체크 → 리다이렉트)
│   └── CartProvider
│       ├── Layout
│       │   ├── BottomNavigation (메뉴/장바구니/주문내역 탭)
│       │   └── CartBadge (장바구니 아이템 수)
│       ├── MenuPage
│       │   ├── CategoryTabs (카테고리 탭 목록)
│       │   └── MenuGrid
│       │       └── MenuCard (메뉴 카드)
│       ├── MenuDetailPage
│       │   ├── MenuInfo (이름, 가격, 설명, 이미지)
│       │   ├── OptionGroupList
│       │   │   └── OptionGroup
│       │   │       └── OptionItem (체크박스/라디오)
│       │   ├── PriceDisplay (실시간 총 가격)
│       │   └── AddToCartButton
│       ├── CartPage
│       │   ├── CartItemList
│       │   │   └── CartItemCard
│       │   │       ├── QuantityControl
│       │   │       └── RemoveButton
│       │   ├── CartSummary (총 금액)
│       │   └── OrderButton
│       ├── OrderConfirmPage
│       │   ├── OrderSummary (최종 확인 목록)
│       │   └── ConfirmButton
│       ├── OrderHistoryPage
│       │   └── OrderList
│       │       └── OrderCard
│       │           ├── OrderStatusBadge
│       │           └── OrderItemList
│       └── ErrorPage
└── ToastProvider
```

### 주요 컴포넌트 상세

#### MenuPage
| 항목 | 내용 |
|------|------|
| API | GET /stores/{storeId}/categories, GET /stores/{storeId}/menus?categoryId= |
| 상태 | selectedCategory, menuList (TanStack Query) |
| 동작 | 카테고리 선택 시 메뉴 목록 갱신, 메뉴 카드 클릭 시 상세 페이지 이동 |

#### MenuDetailPage
| 항목 | 내용 |
|------|------|
| API | GET /menus/{menuId}/options |
| 상태 | selectedOptions (로컬), quantity (로컬), calculatedPrice (파생) |
| 동작 | 옵션 선택/해제 → 가격 재계산, 장바구니 추가 → CartProvider dispatch |
| 검증 | 필수 옵션 선택 여부, 최대 선택 수 초과 여부 |

#### CartPage
| 항목 | 내용 |
|------|------|
| API | 없음 (로컬 상태) |
| 상태 | CartProvider의 cartState |
| 동작 | 수량 변경 → dispatch, 삭제 → dispatch, 주문하기 → /cart/confirm 이동 |

#### OrderConfirmPage
| 항목 | 내용 |
|------|------|
| API | POST /stores/{storeId}/orders |
| 상태 | isSubmitting, orderResult |
| 동작 | 확인 → API 호출 → 성공 시 5초 후 /menu 리다이렉트 |

#### OrderHistoryPage
| 항목 | 내용 |
|------|------|
| API | GET /stores/{storeId}/tables/{tableId}/orders?sessionId= |
| 상태 | orders (TanStack Query, 30초 폴링) |
| 동작 | 자동 갱신, 주문 상태 배지 표시 |

---

## 3. Admin App 컴포넌트

### 페이지 구조 (React Router)

```
/login               → LoginPage
/                    → OrderDashboard (기본 페이지)
/tables              → TableManagementPage
/tables/:tableId     → TableDetailPage
/menus               → MenuManagementPage
/menus/new           → MenuFormPage (등록)
/menus/:menuId/edit  → MenuFormPage (수정)
```

### 컴포넌트 계층

```
AdminApp
├── AuthProvider (Admin)
│   ├── LoginPage
│   │   └── LoginForm
│   └── AuthGuard (인증 체크)
│       ├── AppLayout
│       │   ├── Sidebar (네비게이션)
│       │   └── Header (매장명, 로그아웃)
│       ├── OrderDashboard
│       │   ├── ConnectionStatus (SSE 연결 상태)
│       │   ├── TableGrid
│       │   │   └── TableOrderCard
│       │   │       ├── TableHeader (번호, 총액)
│       │   │       ├── LatestOrderPreview
│       │   │       └── NewOrderBadge
│       │   └── OrderDetailPanel (사이드 패널)
│       │       ├── OrderList
│       │       │   └── OrderCard
│       │       │       ├── OrderStatusBadge
│       │       │       ├── OrderItemList
│       │       │       └── StatusChangeButton
│       │       └── DeleteOrderButton
│       ├── TableManagementPage
│       │   ├── TableList
│       │   │   └── TableRow
│       │   │       ├── SessionStatus
│       │   │       ├── CompleteSessionButton
│       │   │       └── ViewHistoryButton
│       │   ├── AddTableForm
│       │   └── OrderHistoryModal
│       │       ├── DateFilter
│       │       └── HistoryList
│       └── MenuManagementPage
│           ├── CategorySidebar
│           │   └── CategoryItem (드래그 정렬)
│           ├── MenuList
│           │   └── MenuRow
│           │       ├── MenuInfo
│           │       ├── EditButton
│           │       ├── DeleteButton
│           │       └── SortHandle (드래그)
│           └── MenuFormPage
│               ├── MenuBasicForm (이름, 가격, 설명, 카테고리)
│               ├── ImageUploader
│               │   └── UploadProgress
│               └── OptionGroupEditor
│                   └── OptionGroupForm
│                       └── OptionItemRow
└── ToastProvider
```

### 주요 컴포넌트 상세

#### LoginPage
| 항목 | 내용 |
|------|------|
| API | POST /auth/admin/login |
| 상태 | form (React Hook Form), isSubmitting, loginError |
| 검증 | 매장 식별자 필수, 사용자명 필수, 비밀번호 필수 |
| 에러 | 401: "아이디 또는 비밀번호가 올바르지 않습니다", 429: "로그인 시도 제한 초과" |

#### OrderDashboard
| 항목 | 내용 |
|------|------|
| API | GET /stores/{storeId}/orders, SSE /stores/{storeId}/orders/stream |
| 상태 | tables (Map), selectedTableId, connectionState |
| 동작 | SSE 이벤트 수신 → 테이블 카드 업데이트, 카드 클릭 → 사이드 패널 열기 |
| 레이아웃 | 좌측: 테이블 그리드 (70%), 우측: 선택된 테이블 상세 패널 (30%) |

#### OrderDetailPanel
| 항목 | 내용 |
|------|------|
| API | PATCH /orders/{orderId}/status, DELETE /orders/{orderId} |
| 상태 | selectedTable의 orders |
| 동작 | 상태 변경 버튼 → 낙관적 업데이트, 삭제 → 확인 다이얼로그 → API 호출 |

#### TableManagementPage
| 항목 | 내용 |
|------|------|
| API | GET /stores/{storeId}/tables, POST /stores/{storeId}/tables, POST /tables/{tableId}/complete |
| 상태 | tables (TanStack Query), showHistoryModal |
| 동작 | 테이블 추가, 이용 완료 처리, 과거 내역 조회 |

#### MenuManagementPage
| 항목 | 내용 |
|------|------|
| API | GET /stores/{storeId}/categories, GET /stores/{storeId}/menus, DELETE /menus/{menuId} |
| 상태 | categories, menus (TanStack Query), selectedCategory |
| 동작 | 카테고리 선택 → 메뉴 필터, 메뉴 추가/수정/삭제, 순서 드래그 |

#### MenuFormPage
| 항목 | 내용 |
|------|------|
| API | POST /stores/{storeId}/menus, PUT /menus/{menuId}, POST /menus/{menuId}/image, POST /menus/{menuId}/options |
| 상태 | form (React Hook Form + Zod), imageFile, optionGroups |
| 검증 | Zod 스키마 (메뉴명 1-50자, 가격 100-1000000, 이미지 5MB 이하) |
| 동작 | 저장 → 메뉴 생성/수정 → 이미지 업로드 → 옵션 그룹 저장 |

---

## 4. API 연동 매핑

### Customer App → Backend API

| 컴포넌트 | API 엔드포인트 | 메서드 |
|----------|---------------|--------|
| AuthGuard | GET /auth/me | 인증 확인 |
| MenuPage | GET /stores/{storeId}/categories | 카테고리 목록 |
| MenuPage | GET /stores/{storeId}/menus | 메뉴 목록 |
| MenuDetailPage | GET /menus/{menuId}/options | 옵션 조회 |
| OrderConfirmPage | POST /stores/{storeId}/orders | 주문 생성 |
| OrderHistoryPage | GET /stores/{storeId}/tables/{tableId}/orders | 주문 내역 |

### Admin App → Backend API

| 컴포넌트 | API 엔드포인트 | 메서드 |
|----------|---------------|--------|
| LoginPage | POST /auth/admin/login | 로그인 |
| OrderDashboard | GET /stores/{storeId}/orders | 주문 목록 |
| OrderDashboard | GET /stores/{storeId}/orders/stream | SSE 스트림 |
| OrderDetailPanel | PATCH /orders/{orderId}/status | 상태 변경 |
| OrderDetailPanel | DELETE /orders/{orderId} | 주문 삭제 |
| TableManagement | GET /stores/{storeId}/tables | 테이블 목록 |
| TableManagement | POST /stores/{storeId}/tables | 테이블 등록 |
| TableManagement | POST /tables/{tableId}/complete | 이용 완료 |
| TableManagement | GET /stores/{storeId}/tables/{tableId}/history | 과거 내역 |
| MenuManagement | GET /stores/{storeId}/categories | 카테고리 목록 |
| MenuManagement | POST /stores/{storeId}/categories | 카테고리 생성 |
| MenuManagement | GET /stores/{storeId}/menus | 메뉴 목록 |
| MenuFormPage | POST /stores/{storeId}/menus | 메뉴 등록 |
| MenuFormPage | PUT /menus/{menuId} | 메뉴 수정 |
| MenuFormPage | DELETE /menus/{menuId} | 메뉴 삭제 |
| MenuFormPage | POST /menus/{menuId}/image | 이미지 URL 발급 |
| MenuFormPage | POST /menus/{menuId}/options | 옵션 그룹 생성 |

---

## 5. 기술 스택 요약

| 영역 | 기술 | 버전 |
|------|------|------|
| 프레임워크 | React | 18+ |
| 언어 | TypeScript | 5+ |
| 빌드 도구 | Vite | 5+ |
| 패키지 관리 | pnpm workspaces | 8+ |
| UI 라이브러리 | MUI (Material UI) | 5+ |
| 라우팅 | React Router | 6+ |
| 서버 상태 | TanStack Query | 5+ |
| HTTP 클라이언트 | Axios | 1+ |
| 폼 관리 | React Hook Form | 7+ |
| 스키마 검증 | Zod | 3+ |
| 상태 관리 | React Context + useReducer | - |
| PBT 테스트 | fast-check | 3+ |
| 단위 테스트 | Vitest + React Testing Library | - |
