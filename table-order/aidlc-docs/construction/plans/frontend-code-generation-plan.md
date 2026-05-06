# Code Generation Plan — Frontend (개발자 C)

## 개요
Unit 5 (Frontend) 모노레포의 코드 생성 계획입니다.
Shared UI + Customer App + Admin App 3개 패키지를 순차적으로 생성합니다.

## 유닛 컨텍스트
- **담당 스토리**: US-01 ~ US-10 (프론트엔드 UI 부분)
- **의존성**: Auth Service API, Store Service API, Menu Service API, Order Service API
- **기술 스택**: React 18 + TypeScript + Vite + pnpm + MUI + TanStack Query + React Hook Form + Zod + fast-check

## 코드 위치
- **Application Code**: `table-order/frontend/` (워크스페이스 루트 하위)
- **Documentation**: `table-order/aidlc-docs/construction/frontend/code/`

---

## 생성 단계

### Step 1: 프로젝트 구조 셋업 (모노레포 초기화)
- [ ] pnpm-workspace.yaml 생성
- [ ] 루트 package.json (scripts, devDependencies)
- [ ] tsconfig.base.json (공통 TypeScript 설정)
- [ ] .eslintrc.cjs (공통 ESLint 설정)
- [ ] .prettierrc (Prettier 설정)
- [ ] vitest.workspace.ts (Vitest 워크스페이스)
- [ ] .gitignore

### Step 2: Shared 패키지 — 타입 정의
- [ ] packages/shared/package.json
- [ ] packages/shared/tsconfig.json
- [ ] packages/shared/src/types/store.ts (Store, Table, TableSession)
- [ ] packages/shared/src/types/menu.ts (Category, MenuItem, OptionGroup, OptionItem)
- [ ] packages/shared/src/types/order.ts (Order, OrderItem, OrderItemOption, OrderStatus)
- [ ] packages/shared/src/types/auth.ts (AuthState, AdminAuthState, LoginResponse)
- [ ] packages/shared/src/types/cart.ts (CartItem, CartState, SelectedOption)
- [ ] packages/shared/src/types/api.ts (ApiResponse, ApiError, PaginatedResponse)
- [ ] packages/shared/src/types/index.ts (배럴 export)

### Step 3: Shared 패키지 — 유틸리티 함수
- [ ] packages/shared/src/utils/formatPrice.ts
- [ ] packages/shared/src/utils/formatDate.ts
- [ ] packages/shared/src/utils/apiClient.ts (Axios 인스턴스 + 인터셉터)
- [ ] packages/shared/src/utils/storageManager.ts (localStorage 래퍼)
- [ ] packages/shared/src/utils/errorReporter.ts (에러 수집/전송)
- [ ] packages/shared/src/utils/index.ts

### Step 4: Shared 패키지 — 공통 훅
- [ ] packages/shared/src/hooks/useLocalStorage.ts
- [ ] packages/shared/src/hooks/useToast.ts
- [ ] packages/shared/src/hooks/useNetworkStatus.ts
- [ ] packages/shared/src/hooks/index.ts

### Step 5: Shared 패키지 — 공통 컴포넌트
- [ ] packages/shared/src/components/Loading.tsx
- [ ] packages/shared/src/components/Toast/ToastProvider.tsx
- [ ] packages/shared/src/components/ConfirmDialog.tsx
- [ ] packages/shared/src/components/EmptyState.tsx
- [ ] packages/shared/src/components/PriceDisplay.tsx
- [ ] packages/shared/src/components/QuantityControl.tsx
- [ ] packages/shared/src/components/PageErrorBoundary.tsx
- [ ] packages/shared/src/components/index.ts
- [ ] packages/shared/src/index.ts (패키지 메인 export)

### Step 6: Shared 패키지 — 단위 테스트 + PBT
- [ ] packages/shared/src/utils/__tests__/formatPrice.test.ts
- [ ] packages/shared/src/utils/__tests__/formatPrice.pbt.ts (PBT: round-trip)
- [ ] packages/shared/src/utils/__tests__/storageManager.test.ts
- [ ] packages/shared/vitest.config.ts

### Step 7: Customer App — 프로젝트 셋업
- [ ] packages/customer-app/package.json
- [ ] packages/customer-app/tsconfig.json
- [ ] packages/customer-app/vite.config.ts (프록시 설정 포함)
- [ ] packages/customer-app/index.html
- [ ] packages/customer-app/src/main.tsx
- [ ] packages/customer-app/src/App.tsx (라우터 설정)

### Step 8: Customer App — 인증 컨텍스트 (US-01)
- [ ] packages/customer-app/src/contexts/AuthContext.tsx (자동 로그인)
- [ ] packages/customer-app/src/components/AuthGuard.tsx
- [ ] packages/customer-app/src/pages/ErrorPage.tsx

### Step 9: Customer App — 장바구니 컨텍스트 (US-04)
- [ ] packages/customer-app/src/contexts/CartContext.tsx (useReducer + localStorage)
- [ ] packages/customer-app/src/contexts/cartReducer.ts
- [ ] packages/customer-app/src/contexts/__tests__/cartReducer.test.ts
- [ ] packages/customer-app/src/contexts/__tests__/cartReducer.pbt.ts (PBT: invariant, stateful)

### Step 10: Customer App — 메뉴 페이지 (US-02, US-03)
- [ ] packages/customer-app/src/api/menuApi.ts
- [ ] packages/customer-app/src/pages/MenuPage.tsx
- [ ] packages/customer-app/src/components/CategoryTabs.tsx
- [ ] packages/customer-app/src/components/MenuGrid.tsx
- [ ] packages/customer-app/src/components/MenuCard.tsx
- [ ] packages/customer-app/src/pages/MenuDetailPage.tsx
- [ ] packages/customer-app/src/components/OptionGroupList.tsx
- [ ] packages/customer-app/src/components/OptionGroup.tsx

### Step 11: Customer App — 장바구니 & 주문 페이지 (US-04, US-05, US-06)
- [ ] packages/customer-app/src/api/orderApi.ts
- [ ] packages/customer-app/src/pages/CartPage.tsx
- [ ] packages/customer-app/src/components/CartItemCard.tsx
- [ ] packages/customer-app/src/pages/OrderConfirmPage.tsx
- [ ] packages/customer-app/src/pages/OrderHistoryPage.tsx
- [ ] packages/customer-app/src/components/OrderCard.tsx
- [ ] packages/customer-app/src/components/OrderStatusBadge.tsx

### Step 12: Customer App — 레이아웃 & 네비게이션
- [ ] packages/customer-app/src/components/Layout.tsx
- [ ] packages/customer-app/src/components/BottomNavigation.tsx
- [ ] packages/customer-app/src/components/CartBadge.tsx

### Step 13: Admin App — 프로젝트 셋업
- [ ] packages/admin-app/package.json
- [ ] packages/admin-app/tsconfig.json
- [ ] packages/admin-app/vite.config.ts
- [ ] packages/admin-app/index.html
- [ ] packages/admin-app/src/main.tsx
- [ ] packages/admin-app/src/App.tsx (라우터 설정)

### Step 14: Admin App — 인증 & 로그인 (US-07)
- [ ] packages/admin-app/src/contexts/AuthContext.tsx (관리자 JWT)
- [ ] packages/admin-app/src/components/AuthGuard.tsx
- [ ] packages/admin-app/src/api/authApi.ts
- [ ] packages/admin-app/src/pages/LoginPage.tsx
- [ ] packages/admin-app/src/schemas/loginSchema.ts (Zod)

### Step 15: Admin App — 주문 대시보드 (US-08)
- [ ] packages/admin-app/src/api/orderApi.ts
- [ ] packages/admin-app/src/hooks/useSSE.ts
- [ ] packages/admin-app/src/pages/OrderDashboard.tsx
- [ ] packages/admin-app/src/components/TableGrid.tsx
- [ ] packages/admin-app/src/components/TableOrderCard.tsx
- [ ] packages/admin-app/src/components/OrderDetailPanel.tsx
- [ ] packages/admin-app/src/components/OrderStatusBadge.tsx
- [ ] packages/admin-app/src/components/ConnectionStatus.tsx

### Step 16: Admin App — 테이블 관리 (US-09)
- [ ] packages/admin-app/src/api/tableApi.ts
- [ ] packages/admin-app/src/pages/TableManagementPage.tsx
- [ ] packages/admin-app/src/components/TableList.tsx
- [ ] packages/admin-app/src/components/AddTableForm.tsx
- [ ] packages/admin-app/src/components/OrderHistoryModal.tsx
- [ ] packages/admin-app/src/schemas/tableSchema.ts (Zod)

### Step 17: Admin App — 메뉴 관리 (US-10)
- [ ] packages/admin-app/src/api/menuApi.ts
- [ ] packages/admin-app/src/pages/MenuManagementPage.tsx
- [ ] packages/admin-app/src/pages/MenuFormPage.tsx
- [ ] packages/admin-app/src/components/CategorySidebar.tsx
- [ ] packages/admin-app/src/components/MenuList.tsx
- [ ] packages/admin-app/src/components/ImageUploader.tsx
- [ ] packages/admin-app/src/components/OptionGroupEditor.tsx
- [ ] packages/admin-app/src/schemas/menuSchema.ts (Zod)

### Step 18: Admin App — 레이아웃
- [ ] packages/admin-app/src/components/AppLayout.tsx
- [ ] packages/admin-app/src/components/Sidebar.tsx
- [ ] packages/admin-app/src/components/Header.tsx

### Step 19: 코드 생성 요약 문서
- [ ] aidlc-docs/construction/frontend/code/code-summary.md

---

## 스토리 추적

| 스토리 | 구현 Step | 상태 |
|--------|-----------|------|
| US-01 (자동 로그인) | Step 8 | [ ] |
| US-02 (메뉴 조회) | Step 10 | [ ] |
| US-03 (옵션 선택) | Step 10 | [ ] |
| US-04 (장바구니) | Step 9, 11 | [ ] |
| US-05 (주문 생성) | Step 11 | [ ] |
| US-06 (주문 내역) | Step 11 | [ ] |
| US-07 (관리자 인증) | Step 14 | [ ] |
| US-08 (주문 모니터링) | Step 15 | [ ] |
| US-09 (테이블 관리) | Step 16 | [ ] |
| US-10 (메뉴 관리) | Step 17 | [ ] |
