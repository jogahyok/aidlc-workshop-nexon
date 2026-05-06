# Frontend Domain Entities

## 개요
프론트엔드에서 사용하는 도메인 엔티티(타입) 정의입니다.
백엔드 API 응답을 기반으로 하되, 프론트엔드 전용 상태도 포함합니다.

---

## 1. 공통 타입 (Shared)

### Store
```typescript
interface Store {
  id: string;
  name: string;
  description?: string;
}
```

### Table
```typescript
interface Table {
  id: string;
  storeId: string;
  tableNumber: number;
  status: 'active' | 'inactive';
  currentSessionId?: string;
}
```

### TableSession
```typescript
interface TableSession {
  id: string;
  tableId: string;
  storeId: string;
  startedAt: string;       // ISO 8601
  endedAt?: string;        // ISO 8601, null if active
  status: 'active' | 'completed';
}
```

### Category
```typescript
interface Category {
  id: string;
  storeId: string;
  name: string;
  sortOrder: number;
}
```

### MenuItem
```typescript
interface MenuItem {
  id: string;
  categoryId: string;
  storeId: string;
  name: string;
  price: number;
  description?: string;
  imageUrl?: string;
  sortOrder: number;
  optionGroups: OptionGroup[];
}
```

### OptionGroup
```typescript
interface OptionGroup {
  id: string;
  menuItemId: string;
  name: string;
  isRequired: boolean;
  minSelections: number;
  maxSelections: number;
  options: OptionItem[];
}
```

### OptionItem
```typescript
interface OptionItem {
  id: string;
  groupId: string;
  name: string;
  additionalPrice: number;
}
```

### Order
```typescript
interface Order {
  id: string;
  storeId: string;
  tableId: string;
  sessionId: string;
  orderNumber: string;
  status: OrderStatus;
  totalAmount: number;
  items: OrderItem[];
  createdAt: string;       // ISO 8601
  updatedAt: string;       // ISO 8601
}

type OrderStatus = 'pending' | 'preparing' | 'completed';
```

### OrderItem
```typescript
interface OrderItem {
  id: string;
  orderId: string;
  menuName: string;
  quantity: number;
  unitPrice: number;
  options: OrderItemOption[];
  subtotal: number;        // (unitPrice + sum(options.price)) * quantity
}
```

### OrderItemOption
```typescript
interface OrderItemOption {
  id: string;
  orderItemId: string;
  optionName: string;
  additionalPrice: number;
}
```

---

## 2. 프론트엔드 전용 타입

### CartItem (장바구니 항목)
```typescript
interface CartItem {
  cartItemId: string;      // 클라이언트 생성 UUID
  menuItem: MenuItem;
  selectedOptions: SelectedOption[];
  quantity: number;
  itemTotal: number;       // (menuItem.price + sum(selectedOptions.additionalPrice)) * quantity
  addedAt: string;         // ISO 8601
}
```

### SelectedOption (선택된 옵션)
```typescript
interface SelectedOption {
  groupId: string;
  groupName: string;
  optionId: string;
  optionName: string;
  additionalPrice: number;
}
```

### CartState (장바구니 상태)
```typescript
interface CartState {
  items: CartItem[];
  totalAmount: number;     // sum(items.itemTotal)
  itemCount: number;       // sum(items.quantity)
  storeId: string;
  tableId: string;
  sessionId: string;
  lastUpdated: string;     // ISO 8601
  expiresAt: string;       // 세션 만료 시간
}
```

### AuthState (인증 상태)
```typescript
interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  userType: 'admin' | 'table' | null;
  storeId: string | null;
  tableId?: string | null;
  tableNumber?: number | null;
  expiresAt: string | null;
}
```

### AdminAuthState (관리자 인증 상태)
```typescript
interface AdminAuthState {
  isAuthenticated: boolean;
  token: string | null;
  storeId: string | null;
  username: string | null;
  expiresAt: string | null;  // 16시간 만료
}
```

---

## 3. API 응답 타입

### ApiResponse (공통 응답 래퍼)
```typescript
interface ApiResponse<T> {
  data: T;
  message?: string;
}

interface ApiError {
  statusCode: number;
  message: string;
  details?: Record<string, string[]>;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
}
```

### LoginResponse
```typescript
interface AdminLoginResponse {
  accessToken: string;
  expiresAt: string;
  store: Store;
  username: string;
}

interface TableLoginResponse {
  accessToken: string;
  expiresAt: string;
  store: Store;
  table: Table;
  session: TableSession;
}
```

---

## 4. SSE 이벤트 타입 (Admin App)

### OrderEvent
```typescript
type OrderEvent =
  | { type: 'new_order'; data: Order }
  | { type: 'status_changed'; data: { orderId: string; status: OrderStatus } }
  | { type: 'order_deleted'; data: { orderId: string; tableId: string } };
```

---

## 5. 폼 입력 타입

### AdminLoginForm
```typescript
interface AdminLoginForm {
  storeIdentifier: string;
  username: string;
  password: string;
}
```

### MenuForm (메뉴 등록/수정)
```typescript
interface MenuForm {
  name: string;
  price: number;
  description?: string;
  categoryId: string;
  imageFile?: File;
  sortOrder: number;
}
```

### OptionGroupForm
```typescript
interface OptionGroupForm {
  name: string;
  isRequired: boolean;
  minSelections: number;
  maxSelections: number;
  options: OptionItemForm[];
}

interface OptionItemForm {
  name: string;
  additionalPrice: number;
}
```

### TableForm (테이블 등록)
```typescript
interface TableForm {
  tableNumber: number;
  password: string;
}
```
