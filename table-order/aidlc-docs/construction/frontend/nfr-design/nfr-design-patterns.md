# NFR Design Patterns — Frontend (Unit 5)

## 개요
프론트엔드 유닛에 적용되는 NFR 설계 패턴입니다.
성능, 복원력, 보안 패턴을 구체적인 구현 방식으로 정의합니다.

---

## 1. 성능 패턴 (Performance Patterns)

### PP-01: 코드 스플리팅 (Route-Based Code Splitting)

**패턴**: React.lazy + Suspense를 사용한 페이지 단위 지연 로딩

```typescript
// Customer App 라우트 설정
const MenuPage = lazy(() => import('./pages/MenuPage'));
const CartPage = lazy(() => import('./pages/CartPage'));
const OrderHistoryPage = lazy(() => import('./pages/OrderHistoryPage'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/menu" element={<MenuPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/orders" element={<OrderHistoryPage />} />
      </Routes>
    </Suspense>
  );
}
```

**적용 범위**:
- Customer App: MenuPage, MenuDetailPage, CartPage, OrderConfirmPage, OrderHistoryPage
- Admin App: OrderDashboard, TableManagementPage, MenuManagementPage, MenuFormPage

### PP-02: 이미지 최적화 (Lazy Image Loading)

**패턴**: Intersection Observer 기반 이미지 지연 로딩

```typescript
// 메뉴 이미지 컴포넌트
function MenuImage({ src, alt }: { src?: string; alt: string }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && imgRef.current) {
        imgRef.current.src = src || '/placeholder-menu.png';
        observer.disconnect();
      }
    });
    if (imgRef.current) observer.observe(imgRef.current);
    return () => observer.disconnect();
  }, [src]);

  return (
    <Box sx={{ position: 'relative', paddingTop: '66%', bgcolor: 'grey.100' }}>
      <img ref={imgRef} alt={alt} onLoad={() => setIsLoaded(true)}
           style={{ opacity: isLoaded ? 1 : 0, transition: 'opacity 0.3s' }} />
    </Box>
  );
}
```

### PP-03: 캐싱 전략 (TanStack Query Cache Configuration)

**패턴**: 데이터 특성별 차등 캐싱

```typescript
// QueryClient 설정
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,        // 기본 30초
      gcTime: 5 * 60 * 1000,       // 가비지 컬렉션 5분
      retry: 3,                     // GET 요청 3회 재시도
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,                     // POST/PATCH/DELETE 재시도 안 함
    },
  },
});

// 데이터별 staleTime 설정
const CACHE_CONFIG = {
  categories: { staleTime: 5 * 60 * 1000 },   // 카테고리: 5분
  menus: { staleTime: 5 * 60 * 1000 },        // 메뉴: 5분
  orders: { staleTime: 30 * 1000 },            // 주문: 30초
  tables: { staleTime: 60 * 1000 },            // 테이블: 1분
};
```

### PP-04: 렌더링 최적화 (Memoization)

**패턴**: 불필요한 리렌더링 방지

```typescript
// 비용이 큰 계산 메모이제이션
const totalAmount = useMemo(
  () => calculateCartTotal(cartItems),
  [cartItems]
);

// 콜백 메모이제이션 (자식 컴포넌트 리렌더링 방지)
const handleQuantityChange = useCallback(
  (cartItemId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { cartItemId, quantity } });
  },
  [dispatch]
);

// 리스트 아이템 메모이제이션
const MemoizedMenuCard = memo(MenuCard);
```

---

## 2. 복원력 패턴 (Resilience Patterns)

### RP-01: 에러 바운더리 계층 (Error Boundary Hierarchy)

**패턴**: 페이지 레벨 에러 격리

```typescript
// 에러 바운더리 컴포넌트
class PageErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 에러 리포팅 서버 전송
    reportError({ error, errorInfo, page: this.props.pageName });
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback onRetry={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}

// 적용 구조
<App>
  <PageErrorBoundary pageName="menu">
    <MenuPage />
  </PageErrorBoundary>
  <PageErrorBoundary pageName="cart">
    <CartPage />
  </PageErrorBoundary>
</App>
```

### RP-02: API 재시도 패턴 (Selective Retry)

**패턴**: GET 요청만 자동 재시도, 변경 요청은 재시도 안 함

```typescript
// TanStack Query 재시도 설정
function useMenus(storeId: string) {
  return useQuery({
    queryKey: ['menus', storeId],
    queryFn: () => api.getMenus(storeId),
    retry: 3,                                    // GET: 3회 재시도
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10000),
  });
}

function useCreateOrder() {
  return useMutation({
    mutationFn: (data: CreateOrderRequest) => api.createOrder(data),
    retry: 0,                                    // POST: 재시도 안 함
    onError: (error) => {
      showToast('주문에 실패했습니다. 다시 시도해주세요.', 'error');
    },
  });
}
```

### RP-03: SSE 재연결 패턴 (Auto-Reconnect with Backoff)

**패턴**: 연결 끊김 시 자동 재연결, 최대 5회

```typescript
function useSSE(storeId: string) {
  const [connectionState, setConnectionState] = useState<SSEConnectionState>('connecting');
  const reconnectCount = useRef(0);
  const maxReconnects = 5;
  const reconnectInterval = 3000;

  const connect = useCallback(() => {
    const eventSource = new EventSource(`/api/stores/${storeId}/orders/stream`);

    eventSource.onopen = () => {
      setConnectionState('connected');
      reconnectCount.current = 0;
    };

    eventSource.onerror = () => {
      eventSource.close();
      if (reconnectCount.current < maxReconnects) {
        setConnectionState('disconnected');
        reconnectCount.current++;
        setTimeout(connect, reconnectInterval);
      } else {
        setConnectionState('failed');
      }
    };

    eventSource.onmessage = (event) => {
      const orderEvent: OrderEvent = JSON.parse(event.data);
      handleOrderEvent(orderEvent);
    };

    return eventSource;
  }, [storeId]);

  // 컴포넌트 마운트 시 연결, 언마운트 시 해제
  useEffect(() => {
    const es = connect();
    return () => es.close();
  }, [connect]);

  return { connectionState, reconnect: connect };
}
```

### RP-04: 네트워크 상태 감지 (Online/Offline Detection)

**패턴**: 브라우저 네트워크 상태 모니터링

```typescript
function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => { setIsOnline(true); showToast('네트워크 연결됨', 'success'); };
    const handleOffline = () => { setIsOnline(false); showToast('네트워크 연결 끊김', 'warning'); };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

---

## 3. 보안 패턴 (Security Patterns)

### SP-01: 인증 인터셉터 (Auth Interceptor)

**패턴**: Axios 인터셉터로 토큰 자동 주입 및 만료 처리

```typescript
function createAuthenticatedClient(getToken: () => string | null) {
  const client = axios.create({ baseURL: import.meta.env.VITE_API_URL });

  // 요청 인터셉터: 토큰 주입
  client.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // 응답 인터셉터: 401 처리
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        clearAuthStorage();
        window.location.href = '/login'; // 또는 에러 페이지
      }
      return Promise.reject(error);
    }
  );

  return client;
}
```

### SP-02: 토큰 만료 사전 체크 (Proactive Token Check)

**패턴**: API 호출 전 토큰 만료 여부 확인

```typescript
function useAuthGuard() {
  const { token, expiresAt, logout } = useAuth();

  useEffect(() => {
    if (!token || !expiresAt) return;

    const checkExpiry = () => {
      if (new Date(expiresAt).getTime() < Date.now()) {
        logout();
        showToast('세션이 만료되었습니다. 다시 로그인해주세요.', 'info');
      }
    };

    // 1분마다 만료 체크
    const interval = setInterval(checkExpiry, 60 * 1000);
    checkExpiry(); // 즉시 1회 체크

    return () => clearInterval(interval);
  }, [token, expiresAt, logout]);
}
```

### SP-03: 입력 검증 패턴 (Schema-Based Validation)

**패턴**: Zod 스키마 + React Hook Form 통합

```typescript
// 메뉴 등록 폼 스키마
const menuFormSchema = z.object({
  name: z.string().min(1, '메뉴명을 입력해주세요').max(50, '50자 이내로 입력해주세요'),
  price: z.number().min(100, '100원 이상 입력해주세요').max(1000000, '100만원 이하로 입력해주세요'),
  description: z.string().max(200, '200자 이내로 입력해주세요').optional(),
  categoryId: z.string().min(1, '카테고리를 선택해주세요'),
});

type MenuFormData = z.infer<typeof menuFormSchema>;

// 폼 컴포넌트에서 사용
const { register, handleSubmit, formState: { errors } } = useForm<MenuFormData>({
  resolver: zodResolver(menuFormSchema),
});
```

### SP-04: 환경 변수 보안 (Environment Variable Pattern)

**패턴**: API URL 등 설정값을 환경 변수로 관리

```typescript
// .env.development
VITE_API_URL=http://localhost:8000/api
VITE_APP_ENV=development

// .env.production
VITE_API_URL=https://api.tableorder.example.com
VITE_APP_ENV=production

// 사용
const apiUrl = import.meta.env.VITE_API_URL;
const isProduction = import.meta.env.VITE_APP_ENV === 'production';

// 프로덕션에서 콘솔 로그 비활성화
if (isProduction) {
  console.log = () => {};
  console.debug = () => {};
}
```

---

## 4. 데이터 동기화 패턴 (Data Sync Patterns)

### DS-01: 낙관적 업데이트 (Optimistic Update)

**패턴**: 서버 응답 전 UI 즉시 반영, 실패 시 롤백

**적용 대상**: 주문 상태 변경, 메뉴 순서 조정, 장바구니 수량 변경

```typescript
// 주문 상태 변경 (Admin)
const updateStatusMutation = useMutation({
  mutationFn: ({ orderId, status }: { orderId: string; status: OrderStatus }) =>
    api.updateOrderStatus(orderId, status),
  onMutate: async ({ orderId, status }) => {
    await queryClient.cancelQueries({ queryKey: ['orders'] });
    const previous = queryClient.getQueryData<Order[]>(['orders']);
    queryClient.setQueryData<Order[]>(['orders'], (old) =>
      old?.map(o => o.id === orderId ? { ...o, status } : o)
    );
    return { previous };
  },
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(['orders'], context?.previous);
    showToast('상태 변경에 실패했습니다', 'error');
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['orders'] });
  },
});
```

### DS-02: 폴링 패턴 (Polling for Customer Orders)

**패턴**: 주문 내역 페이지에서 30초 간격 자동 갱신

```typescript
function useOrderHistory(storeId: string, tableId: string, sessionId: string) {
  return useQuery({
    queryKey: ['orders', tableId, sessionId],
    queryFn: () => api.getTableOrders(storeId, tableId, sessionId),
    refetchInterval: 30 * 1000,              // 30초 폴링
    refetchIntervalInBackground: false,      // 탭 비활성 시 중지
    staleTime: 10 * 1000,                    // 10초간 fresh
  });
}
```

### DS-03: localStorage 동기화 (Cross-Tab Sync)

**패턴**: 탭 간 인증 상태 동기화

```typescript
function useStorageSync(key: string, onUpdate: (value: string | null) => void) {
  useEffect(() => {
    const handler = (event: StorageEvent) => {
      if (event.key === key) {
        onUpdate(event.newValue);
      }
    };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, [key, onUpdate]);
}

// 사용: 다른 탭에서 로그아웃 시 현재 탭도 로그아웃
useStorageSync('auth_token', (newValue) => {
  if (!newValue) logout();
});
```
