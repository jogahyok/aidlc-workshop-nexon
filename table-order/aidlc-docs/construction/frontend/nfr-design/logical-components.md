# Logical Components — Frontend (Unit 5)

## 개요
프론트엔드 유닛의 논리적 인프라 컴포넌트 정의입니다.
비즈니스 로직과 별개로, 시스템 품질을 보장하는 횡단 관심사(cross-cutting concerns) 컴포넌트입니다.

---

## 1. API Client Layer

### 역할
- 모든 백엔드 API 통신의 단일 진입점
- 인증 토큰 자동 주입
- 에러 응답 표준화
- 요청/응답 로깅 (개발 모드)

### 구성

```
shared/src/utils/
├── apiClient.ts          # Axios 인스턴스 생성 + 인터셉터
├── apiError.ts           # 에러 타입 정의 + 파싱
└── apiConfig.ts          # 환경별 설정 (baseURL, timeout)
```

### 인터페이스

```typescript
// apiClient.ts
export function createApiClient(config: ApiClientConfig): AxiosInstance;

interface ApiClientConfig {
  baseUrl: string;
  getToken: () => string | null;
  onUnauthorized: () => void;
  onNetworkError: () => void;
  timeout?: number;          // 기본 10초
}
```

### 설정값
- **timeout**: 10초 (기본), 이미지 업로드: 60초
- **재시도**: GET 3회 (지수 백오프 1s, 2s, 4s), POST/PATCH/DELETE 0회
- **동시 요청 제한**: 없음 (TanStack Query deduplication으로 충분)

---

## 2. Auth Guard

### 역할
- 인증 필요 라우트 보호
- 미인증 사용자 리다이렉트
- 토큰 만료 사전 감지
- 탭 간 인증 상태 동기화

### 구성

```
shared/src/hooks/
├── useAuth.ts            # 인증 상태 관리 훅
└── useAuthGuard.ts       # 라우트 보호 훅

customer-app/src/contexts/
└── AuthContext.tsx        # Customer 인증 Context (자동 로그인)

admin-app/src/contexts/
└── AuthContext.tsx        # Admin 인증 Context (로그인 폼)
```

### 동작 흐름

```
Text Alternative:
[App Load] → AuthProvider 초기화
  → localStorage에서 토큰 읽기
  → 토큰 없음 → 에러 페이지 (Customer) / 로그인 페이지 (Admin)
  → 토큰 있음 → 만료 체크
    → 만료됨 → 토큰 삭제 + 에러/로그인 페이지
    → 유효 → GET /auth/me 호출
      → 성공 → 인증 상태 설정 + 보호된 라우트 접근 허용
      → 실패 → 토큰 삭제 + 에러/로그인 페이지
```

### 설정값
- **만료 체크 간격**: 60초
- **토큰 저장 키**: `auth_token_{storeId}` (Customer), `admin_token_{storeId}` (Admin)
- **탭 동기화**: storage 이벤트 리스닝

---

## 3. Error Reporter

### 역할
- 클라이언트 에러 수집
- 구조화된 에러 로그 생성
- 서버 전송 (비동기, 비차단)
- 민감 정보 필터링

### 구성

```
shared/src/utils/
├── errorReporter.ts      # 에러 수집 + 전송
└── errorFilter.ts        # 민감 정보 필터링
```

### 인터페이스

```typescript
interface ErrorReport {
  timestamp: string;
  errorType: 'runtime' | 'network' | 'validation' | 'unhandled';
  message: string;
  stack?: string;
  componentStack?: string;
  url: string;
  userAgent: string;
  appVersion: string;
  context?: Record<string, unknown>;  // 민감 정보 제외
}

export function reportError(report: ErrorReport): void;
export function setupGlobalErrorHandler(): void;
```

### 설정값
- **전송 엔드포인트**: POST /errors
- **배치 전송**: 5개 모이면 또는 10초마다 전송
- **실패 시**: 무시 (앱 동작에 영향 없음)
- **필터링**: token, password, authorization 헤더 제거
- **프로덕션만**: 개발 모드에서는 콘솔 출력만

---

## 4. SSE Manager

### 역할
- SSE 연결 생명주기 관리
- 자동 재연결 (지수 백오프)
- 이벤트 파싱 및 디스패치
- 연결 상태 모니터링

### 구성

```
admin-app/src/hooks/
└── useSSE.ts             # SSE 연결 관리 훅

admin-app/src/utils/
└── sseManager.ts         # SSE 연결 로직
```

### 인터페이스

```typescript
interface SSEManagerConfig {
  url: string;
  onEvent: (event: OrderEvent) => void;
  onConnectionChange: (state: SSEConnectionState) => void;
  maxReconnects?: number;       // 기본 5
  reconnectInterval?: number;   // 기본 3000ms
}

type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'failed';

export function useSSE(config: SSEManagerConfig): {
  connectionState: SSEConnectionState;
  reconnect: () => void;
  disconnect: () => void;
};
```

### 설정값
- **재연결 간격**: 3초
- **최대 재연결 시도**: 5회
- **연결 타임아웃**: 10초
- **하트비트 감지**: 서버에서 30초마다 ping 이벤트 전송 (미수신 시 재연결)

---

## 5. Storage Manager

### 역할
- localStorage 접근 추상화
- JSON 직렬화/역직렬화
- 만료 시간 관리
- 타입 안전한 접근

### 구성

```
shared/src/utils/
└── storageManager.ts     # localStorage 래퍼

shared/src/hooks/
└── useLocalStorage.ts    # React 훅 래퍼
```

### 인터페이스

```typescript
interface StorageItem<T> {
  value: T;
  expiresAt?: string;     // ISO 8601, undefined = 영구
  createdAt: string;
}

export class StorageManager {
  static get<T>(key: string): T | null;
  static set<T>(key: string, value: T, ttlMs?: number): void;
  static remove(key: string): void;
  static isExpired(key: string): boolean;
  static clearExpired(): void;
}

// React 훅
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
  ttlMs?: number
): [T, (value: T) => void, () => void];
```

### 설정값
- **장바구니 키**: `cart_{storeId}_{tableId}`
- **토큰 키**: `auth_token_{storeId}`, `auth_expires_{storeId}`
- **만료 체크**: 앱 로드 시 + 접근 시 자동 체크
- **용량 관리**: 저장 실패 시 (QuotaExceeded) 만료된 항목 정리 후 재시도

---

## 6. Toast Notification System

### 역할
- 사용자 피드백 알림 표시
- 성공/에러/경고/정보 구분
- 자동 닫힘 + 수동 닫기
- 중복 알림 방지

### 구성

```
shared/src/components/
└── ToastProvider.tsx     # Toast Context + 렌더링

shared/src/hooks/
└── useToast.ts           # Toast 표시 훅
```

### 인터페이스

```typescript
interface ToastOptions {
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
  duration?: number;       // 기본 3000ms, error: 5000ms
  action?: { label: string; onClick: () => void };
}

export function useToast(): {
  showToast: (options: ToastOptions) => void;
  closeToast: (id: string) => void;
};
```

### 설정값
- **기본 표시 시간**: success/info 3초, warning 4초, error 5초
- **최대 동시 표시**: 3개
- **위치**: 화면 하단 중앙 (Customer), 우측 상단 (Admin)
- **중복 방지**: 동일 메시지 2초 이내 중복 표시 안 함

---

## 7. 컴포넌트 의존성 다이어그램

```
Text Alternative:
API Client Layer ← Auth Guard (토큰 주입)
API Client Layer ← Error Reporter (에러 전송)
API Client Layer ← TanStack Query (데이터 페칭)

Auth Guard → Storage Manager (토큰 읽기/쓰기)
Auth Guard → Toast System (만료 알림)

SSE Manager → Auth Guard (인증 헤더)
SSE Manager → Toast System (연결 상태 알림)

Storage Manager ← Cart Context (장바구니 저장)
Storage Manager ← Auth Guard (토큰 저장)

Error Reporter ← Error Boundary (에러 캡처)
Error Reporter ← API Client (네트워크 에러)

Toast System ← 모든 컴포넌트 (사용자 피드백)
```

---

## 8. 초기화 순서

```
Text Alternative:
1. Environment Config 로드 (VITE_API_URL, VITE_APP_ENV)
2. Storage Manager 초기화 + 만료 항목 정리
3. Error Reporter 초기화 + 글로벌 에러 핸들러 등록
4. API Client 생성 (인터셉터 설정)
5. Auth Provider 초기화 (토큰 확인 + 유효성 검증)
6. Toast Provider 마운트
7. QueryClient Provider 마운트
8. Router 마운트 + Auth Guard 활성화
9. (Admin만) SSE Manager 연결
```

---

## Security Baseline Compliance

| Rule | Status | 적용 컴포넌트 |
|------|--------|--------------|
| SECURITY-03 | Compliant | Error Reporter — 구조화된 로깅, 민감 정보 필터링 |
| SECURITY-04 | Compliant | 서버 설정 (프론트엔드는 HTTPS 강제만) |
| SECURITY-05 | Compliant | API Client — Zod 스키마 검증, 입력 sanitization |
| SECURITY-08 | Compliant | Auth Guard — 모든 라우트 인증 체크, 401 처리 |
| SECURITY-09 | Compliant | Error Reporter — 프로덕션 에러 메시지 일반화 |
| SECURITY-12 | Compliant | Auth Guard — 토큰 만료 관리, 로그아웃 처리 |
| SECURITY-15 | Compliant | Error Boundary — 전역 에러 핸들러, fail-safe 기본값 |

## PBT Compliance

| Rule | Status | 적용 내용 |
|------|--------|-----------|
| PBT-09 | Compliant | fast-check 프레임워크 선택, 논리적 컴포넌트에 영향 없음 |
| 기타 | N/A | NFR Design 단계에서는 PBT 구현 해당 없음 (Code Generation에서 적용) |
