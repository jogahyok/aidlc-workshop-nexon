# Frontend Business Logic Model

## 개요
프론트엔드의 핵심 비즈니스 로직 모델입니다.
상태 관리, 데이터 흐름, 주요 알고리즘을 정의합니다.

---

## 1. 상태 관리 아키텍처

### 상태 관리 전략
- **전역 상태**: React Context + useReducer (인증, 장바구니)
- **서버 상태**: TanStack Query (API 데이터 캐싱, 동기화)
- **로컬 상태**: useState (UI 상태, 폼 입력)
- **영속 상태**: localStorage (토큰, 장바구니)

### Context 구조

```
App
├── AuthProvider (인증 상태)
│   ├── Customer: 자동 로그인 토큰
│   └── Admin: 관리자 JWT 토큰
├── CartProvider (장바구니 상태 - Customer App만)
│   ├── items: CartItem[]
│   ├── totalAmount: number
│   └── localStorage 동기화
└── Pages (TanStack Query로 서버 데이터 관리)
```

---

## 2. 장바구니 상태 머신

### 상태 전이 다이어그램

```
Text Alternative:
[Empty] --addItem--> [HasItems]
[HasItems] --addItem--> [HasItems]
[HasItems] --removeItem(last)--> [Empty]
[HasItems] --removeItem--> [HasItems]
[HasItems] --updateQuantity--> [HasItems]
[HasItems] --clearCart--> [Empty]
[HasItems] --submitOrder--> [Submitting]
[Submitting] --success--> [Empty] (장바구니 비우기 + 주문 번호 표시)
[Submitting] --failure--> [HasItems] (에러 표시 + 장바구니 유지)
```

### Cart Reducer Actions

```typescript
type CartAction =
  | { type: 'ADD_ITEM'; payload: { menuItem: MenuItem; options: SelectedOption[]; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: { cartItemId: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { cartItemId: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_FROM_STORAGE'; payload: CartState }
  | { type: 'RESET_EXPIRED' };
```

### 금액 계산 알고리즘

```typescript
function calculateItemTotal(menuPrice: number, options: SelectedOption[], quantity: number): number {
  const optionsTotal = options.reduce((sum, opt) => sum + opt.additionalPrice, 0);
  return (menuPrice + optionsTotal) * quantity;
}

function calculateCartTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.itemTotal, 0);
}
```

---

## 3. 인증 플로우

### Customer App 자동 로그인 플로우

```
Text Alternative:
1. App 로드
2. localStorage에서 토큰 확인
3. 토큰 없음 → 에러 화면 ("관리자에게 문의")
4. 토큰 있음 → 만료 시간 체크
5. 만료됨 → 에러 화면
6. 유효 → GET /auth/me 호출
7. 성공 → 인증 상태 설정 + 메뉴 화면
8. 실패 → localStorage 클리어 + 에러 화면
```

### Admin App 로그인 플로우

```
Text Alternative:
1. 로그인 폼 표시
2. 사용자 입력 (매장 식별자, 사용자명, 비밀번호)
3. 클라이언트 검증 (빈 값 체크)
4. POST /auth/admin/login 호출
5. 성공 → 토큰 저장 + 대시보드 이동
6. 실패 (401) → 에러 메시지 표시
7. 실패 (429) → 잠금 안내 메시지 + 입력 비활성화
```

### 토큰 만료 처리

```typescript
function isTokenExpired(expiresAt: string): boolean {
  return new Date(expiresAt).getTime() < Date.now();
}

// API 인터셉터에서 401 처리
function handleUnauthorized(): void {
  clearAuthStorage();
  redirectToLogin();
}
```

---

## 4. 주문 생성 플로우

### 주문 데이터 변환

```typescript
function cartToOrderRequest(cart: CartState): CreateOrderRequest {
  return {
    tableId: cart.tableId,
    sessionId: cart.sessionId,
    items: cart.items.map(item => ({
      menuItemId: item.menuItem.id,
      menuName: item.menuItem.name,
      quantity: item.quantity,
      unitPrice: item.menuItem.price,
      options: item.selectedOptions.map(opt => ({
        optionItemId: opt.optionId,
        optionName: opt.optionName,
        additionalPrice: opt.additionalPrice,
      })),
    })),
    totalAmount: cart.totalAmount,
  };
}
```

### 주문 확정 시퀀스

```
Text Alternative:
1. 사용자: 주문 확정 버튼 클릭
2. UI: 최종 확인 모달 표시
3. 사용자: 확인 버튼 클릭
4. UI: 로딩 상태 + 버튼 비활성화
5. API: POST /stores/{storeId}/orders
6a. 성공:
    - 주문 번호 표시 (성공 모달)
    - 5초 카운트다운
    - 장바구니 비우기 (localStorage 포함)
    - 메뉴 화면으로 리다이렉트
6b. 실패:
    - 에러 Toast 표시
    - 장바구니 유지
    - 버튼 재활성화
```

---

## 5. SSE 실시간 주문 스트림 (Admin App)

### SSE 연결 관리 로직

```typescript
interface SSEConfig {
  url: string;                    // /stores/{storeId}/orders/stream
  reconnectInterval: number;      // 3000ms
  maxReconnectAttempts: number;   // 5
}

// 연결 상태
type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'failed';
```

### SSE 이벤트 처리

```typescript
function handleOrderEvent(event: OrderEvent, dispatch: Dispatch): void {
  switch (event.type) {
    case 'new_order':
      dispatch({ type: 'ADD_ORDER', payload: event.data });
      highlightTable(event.data.tableId);
      break;
    case 'status_changed':
      dispatch({ type: 'UPDATE_ORDER_STATUS', payload: event.data });
      break;
    case 'order_deleted':
      dispatch({ type: 'REMOVE_ORDER', payload: event.data });
      recalculateTableTotal(event.data.tableId);
      break;
  }
}
```

### 대시보드 데이터 구조

```typescript
interface DashboardState {
  tables: Map<string, TableDashboardData>;
  connectionState: SSEConnectionState;
  reconnectCount: number;
}

interface TableDashboardData {
  table: Table;
  orders: Order[];
  totalAmount: number;
  latestOrder?: Order;
  isHighlighted: boolean;       // 신규 주문 강조
  hasNewOrder: boolean;         // NEW 배지
}
```

---

## 6. Customer App 폴링 로직 (주문 내역)

### 폴링 전략

```typescript
interface PollingConfig {
  interval: number;              // 30000ms (30초)
  enabled: boolean;              // 주문 내역 페이지에서만 true
  pauseOnHidden: boolean;       // 탭 비활성 시 일시정지
}
```

### 구현 패턴 (TanStack Query)

```typescript
// 주문 내역 페이지에서만 30초 간격 자동 갱신
useQuery({
  queryKey: ['orders', tableId, sessionId],
  queryFn: () => fetchTableOrders(storeId, tableId, sessionId),
  refetchInterval: 30000,        // 30초
  refetchIntervalInBackground: false,  // 탭 비활성 시 중지
});
```

---

## 7. 이미지 업로드 플로우 (Admin App)

### Presigned URL 업로드 시퀀스

```
Text Alternative:
1. 사용자: 이미지 파일 선택
2. 클라이언트: 파일 검증 (크기 5MB 이하, 형식 jpg/png/webp)
3. API: POST /menus/{menuId}/image → presigned URL 수신
4. 클라이언트: PUT presigned URL로 S3 직접 업로드
5. 업로드 중: 프로그레스 바 표시
6a. 성공: 이미지 미리보기 표시 + 메뉴 데이터에 imageUrl 반영
6b. 실패: 에러 메시지 + 재시도 버튼
```

---

## 8. 에러 처리 전략

### 에러 분류 및 처리

| HTTP 상태 | 분류 | 처리 |
|-----------|------|------|
| 400 | 입력 검증 에러 | 필드별 인라인 에러 메시지 |
| 401 | 인증 만료 | 자동 로그아웃 + 로그인 리다이렉트 |
| 403 | 권한 없음 | "접근 권한이 없습니다" Toast |
| 404 | 리소스 없음 | "요청한 데이터를 찾을 수 없습니다" Toast |
| 409 | 충돌 | 상황별 메시지 (예: "이미 처리된 주문입니다") |
| 429 | 요청 제한 | "잠시 후 다시 시도해주세요" + 입력 비활성화 |
| 5xx | 서버 에러 | "일시적인 오류입니다" Toast + 재시도 버튼 |
| Network | 네트워크 에러 | "네트워크 연결을 확인해주세요" Toast |

### 글로벌 에러 핸들러 (Axios Interceptor)

```typescript
function setupErrorInterceptor(axiosInstance: AxiosInstance): void {
  axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        handleUnauthorized();
      }
      return Promise.reject(error);
    }
  );
}
```

---

## 9. 낙관적 업데이트 패턴

### 적용 대상
- 주문 상태 변경 (Admin)
- 메뉴 순서 조정 (Admin)
- 장바구니 수량 변경 (Customer)

### 패턴

```typescript
// TanStack Query 낙관적 업데이트
useMutation({
  mutationFn: updateOrderStatus,
  onMutate: async (newStatus) => {
    // 1. 진행 중인 쿼리 취소
    await queryClient.cancelQueries(['orders']);
    // 2. 이전 상태 스냅샷
    const previous = queryClient.getQueryData(['orders']);
    // 3. 낙관적으로 UI 업데이트
    queryClient.setQueryData(['orders'], (old) => optimisticUpdate(old, newStatus));
    return { previous };
  },
  onError: (err, variables, context) => {
    // 4. 실패 시 롤백
    queryClient.setQueryData(['orders'], context.previous);
    showErrorToast('상태 변경에 실패했습니다');
  },
  onSettled: () => {
    // 5. 성공/실패 후 서버 데이터로 동기화
    queryClient.invalidateQueries(['orders']);
  },
});
```
