# 비즈니스 로직 모델 — Auth Service + Store Service

## Auth Service 비즈니스 로직

### 관리자 로그인 플로우
```
Input: store_code, username, password
  |
  v
[1] Store 조회 (store_code → store_id)
  |-- 실패 → AUTH_001 (매장 없음)
  v
[2] 잠금 상태 확인 (store_id + username, 최근 15분 실패 >= 5)
  |-- 잠금 → AUTH_003 (계정 잠금)
  v
[3] Admin 조회 (store_id + username)
  |-- 없음 → AUTH_002 (인증 실패) + LoginAttempt 기록
  v
[4] 비밀번호 검증 (bcrypt.verify)
  |-- 실패 → AUTH_002 (인증 실패) + LoginAttempt(success=false) 기록
  v
[5] LoginAttempt(success=true) 기록
  |
  v
[6] JWT 토큰 생성 (sub=admin_id, store_id, type='admin', exp=now+16h)
  |
  v
Output: { access_token, token_type, expires_at }
```

### 테이블 로그인 플로우
```
Input: store_code, table_number, password
  |
  v
[1] Store 조회 (store_code → store_id)
  |-- 실패 → AUTH_001 (매장 없음)
  v
[2] 잠금 상태 확인 (store_id + table_number, 최근 15분 실패 >= 5)
  |-- 잠금 → AUTH_003 (계정 잠금)
  v
[3] Table 조회 (store_id + table_number)
  |-- 없음 → AUTH_006 (테이블 없음) + LoginAttempt 기록
  v
[4] TableCredential 조회 (table_id)
  |
  v
[5] 비밀번호 검증 (bcrypt.verify)
  |-- 실패 → AUTH_002 (인증 실패) + LoginAttempt(success=false) 기록
  v
[6] LoginAttempt(success=true) 기록
  |
  v
[7] 현재 active 세션 확인
  |-- 없음 → Store Service에 세션 생성 요청 (최초 로그인)
  v
[8] JWT 토큰 생성 (sub=table_id, store_id, type='table', table_number, exp=now+16h)
  |
  v
Output: { access_token, token_type, expires_at, table_info }
```

### 토큰 검증 플로우
```
Input: Authorization header (Bearer token)
  |
  v
[1] 토큰 파싱 및 서명 검증
  |-- 실패 → AUTH_005 (토큰 무효)
  v
[2] 만료 시간 검증 (exp > now)
  |-- 만료 → AUTH_004 (토큰 만료)
  v
[3] Payload 추출 (sub, store_id, type)
  |
  v
Output: { user_id, store_id, user_type, table_number? }
```

---

## Store Service 비즈니스 로직

### 매장 등록 플로우
```
Input: name, code, admin_username, admin_password
  |
  v
[1] code 중복 확인
  |-- 중복 → STORE_001
  v
[2] Store 생성 (name, code)
  |
  v
[3] Admin 계정 생성 (store_id, username, bcrypt(password))
  |
  v
Output: { store_id, store_code, admin_username }
```

### 테이블 등록 플로우
```
Input: store_id, table_number, password
  |
  v
[1] 테이블 번호 중복 확인 (store_id + table_number)
  |-- 중복 → STORE_002
  v
[2] Table 생성 (store_id, table_number)
  |
  v
[3] TableCredential 생성 (table_id, store_id, bcrypt(password))
  |
  v
Output: { table_id, table_number }
```

### 세션 시작 플로우
```
Input: table_id, store_id
  |
  v
[1] 현재 active 세션 확인 (table_id + status='active')
  |-- 있음 → 기존 세션 반환 (새로 생성하지 않음)
  v
[2] TableSession 생성 (table_id, store_id, status='active', started_at=now)
  |
  v
Output: { session_id, table_id, started_at }
```

### 세션 종료 (이용 완료) 플로우
```
Input: store_id, table_id (관리자 인증 필수)
  |
  v
[1] 현재 active 세션 조회 (table_id + status='active')
  |-- 없음 → STORE_004 (이미 종료됨)
  v
[2] Order Service에 주문 아카이브 요청 (HTTP POST /internal/orders/archive)
  |   Body: { session_id }
  |-- 실패 → STORE_005 (아카이브 실패, 세션 종료 중단)
  v
[3] 세션 상태 변경 (status='completed', completed_at=now)
  |
  v
Output: { session_id, completed_at, message: "이용 완료 처리되었습니다" }
```

### 현재 세션 조회 플로우
```
Input: table_id
  |
  v
[1] active 세션 조회 (table_id + status='active')
  |-- 없음 → null (세션 없음 = 첫 주문 대기 상태)
  v
Output: { session_id, started_at } 또는 null
```

---

## Auth ↔ Store 연동 로직

### 테이블 로그인 시 세션 자동 생성
1. Auth Service에서 테이블 인증 성공
2. Auth Service가 Store Service의 `get_current_session(table_id)` 호출
3. active 세션이 없으면 Store Service의 `start_new_session(table_id)` 호출
4. 세션 정보를 토큰 응답에 포함

### 세션 종료 후 새 세션 시작 (Order Service 연동)
1. 관리자가 이용 완료 처리 (Store Service)
2. 세션 종료됨 → 태블릿은 메뉴 화면 유지
3. 새 고객이 주문 생성 시 (Order Service)
4. Order Service가 Store Service의 `get_current_session(table_id)` 호출
5. active 세션 없음 → Store Service의 `start_new_session(table_id)` 호출
6. 새 세션 ID로 주문 생성

---

## Testable Properties (PBT-01)

### Auth Service
| 속성 | 카테고리 | 설명 |
|------|----------|------|
| JWT Round-trip | Round-trip | encode(payload) → decode(token) = payload |
| Password Hash Round-trip | Easy verification | verify(password, hash(password)) = true |
| Login Attempt Invariant | Invariant | 실패 횟수 < 5 → 잠금 아님, 실패 횟수 >= 5 (15분 내) → 잠금 |
| Token Expiry Invariant | Invariant | now < exp → 유효, now >= exp → 만료 |

### Store Service
| 속성 | 카테고리 | 설명 |
|------|----------|------|
| Session State Machine | Stateful | active → completed (단방향), 테이블당 active 최대 1개 |
| Table Number Uniqueness | Invariant | 동일 매장 내 테이블 번호 중복 불가 |
| Session Lifecycle Idempotence | Idempotence | 이미 active 세션 있을 때 start_session 호출 = 기존 세션 반환 |
