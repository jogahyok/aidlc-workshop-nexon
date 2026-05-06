# Logical Components — Auth Service + Store Service

## 미들웨어 스택 (요청 처리 순서)

```
1. CORS Middleware          — 허용 오리진 검증
2. Request ID Middleware    — UUID 생성/전파
3. Logging Middleware       — 요청/응답 로깅
4. Exception Handler        — 글로벌 예외 처리
5. Auth Dependency          — JWT 토큰 검증 (Depends)
6. Store Access Dependency  — 매장 격리 검증 (Depends)
```

---

## 의존성 주입 패턴

### FastAPI Depends 기반 DI

```python
# 계층 구조
Router (API 엔드포인트)
  └── Depends: get_current_user / get_current_admin
  └── Depends: verify_store_access
  └── Depends: get_db_connection
        └── Service Layer (비즈니스 로직)
              └── DB Query Functions (Raw SQL)
```

### 주요 의존성

| 의존성 | 역할 | 스코프 |
|--------|------|--------|
| `get_db_connection` | DB 커넥션 풀에서 커넥션 획득/반환 | 요청 단위 |
| `get_current_user` | JWT 토큰 검증, 사용자 정보 추출 | 요청 단위 |
| `get_current_admin` | 관리자 권한 검증 | 요청 단위 |
| `verify_store_access` | 매장 접근 권한 검증 | 요청 단위 |
| `get_http_client` | 서비스 간 HTTP 클라이언트 | 앱 수명 |

---

## 설정 관리 패턴

### Pydantic Settings 기반

```python
class Settings(BaseSettings):
    # Database
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str
    
    # JWT
    jwt_secret_key: str  # 최소 32자
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 16
    
    # Rate Limiting
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15
    
    # Service URLs
    order_service_url: str
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    model_config = SettingsConfigDict(env_file=".env")
```

**환경별 설정:**
- Development: `.env` 파일
- Production: 환경변수 (Docker/ECS)
- Testing: 테스트 전용 설정 오버라이드

---

## 프로젝트 구조 (논리적 컴포넌트 매핑)

### Auth Service
```
services/auth-service/
├── app/
│   ├── main.py                 # FastAPI 앱 초기화, 미들웨어 등록
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # 공통 의존성 (get_db, get_current_user)
│   │   └── routes/
│   │       ├── auth.py         # 로그인/토큰 엔드포인트
│   │       └── health.py       # 헬스체크
│   ├── core/
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── security.py         # JWT 생성/검증, bcrypt
│   │   └── exceptions.py       # 커스텀 예외 클래스
│   ├── db/
│   │   ├── connection.py       # 커넥션 풀 관리
│   │   ├── queries/
│   │   │   ├── admin_queries.py
│   │   │   ├── table_credential_queries.py
│   │   │   └── login_attempt_queries.py
│   │   └── mappers/
│   │       ├── admin_mapper.py
│   │       └── login_attempt_mapper.py
│   ├── models/
│   │   ├── admin.py            # Admin 도메인 모델
│   │   ├── table_credential.py
│   │   └── login_attempt.py
│   ├── schemas/
│   │   ├── auth.py             # 요청/응답 Pydantic 스키마
│   │   └── common.py           # 공통 스키마 (에러 응답 등)
│   ├── services/
│   │   ├── auth_service.py     # 인증 비즈니스 로직
│   │   └── login_attempt_service.py
│   └── middleware/
│       ├── request_id.py       # Request ID 미들웨어
│       └── logging.py          # 로깅 미들웨어
├── tests/
│   ├── conftest.py
│   ├── test_auth_service.py
│   ├── test_security.py        # PBT: JWT round-trip
│   └── test_login_attempts.py  # PBT: 잠금 invariant
├── migrations/
│   └── 001_create_auth_tables.sql
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Store Service
```
services/store-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── stores.py       # 매장 관리 엔드포인트
│   │       ├── tables.py       # 테이블 관리 엔드포인트
│   │       ├── sessions.py     # 세션 관리 엔드포인트
│   │       └── health.py
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── queries/
│   │   │   ├── store_queries.py
│   │   │   ├── table_queries.py
│   │   │   └── session_queries.py
│   │   └── mappers/
│   │       ├── store_mapper.py
│   │       ├── table_mapper.py
│   │       └── session_mapper.py
│   ├── models/
│   │   ├── store.py
│   │   ├── table.py
│   │   └── table_session.py
│   ├── schemas/
│   │   ├── store.py
│   │   ├── table.py
│   │   └── session.py
│   ├── services/
│   │   ├── store_service.py
│   │   ├── table_service.py
│   │   └── session_service.py
│   ├── external/
│   │   └── order_client.py    # Order Service HTTP 클라이언트 (재시도 포함)
│   └── middleware/
│       ├── request_id.py
│       └── logging.py
├── tests/
│   ├── conftest.py
│   ├── test_store_service.py
│   ├── test_table_service.py
│   ├── test_session_service.py # PBT: 세션 상태 머신
│   └── test_order_client.py
├── migrations/
│   └── 001_create_store_tables.sql
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## 공통 패턴 요약

| 패턴 | 구현 위치 | 목적 |
|------|-----------|------|
| Request ID | middleware/request_id.py | 요청 추적, 서비스 간 전파 |
| Global Exception Handler | main.py | 표준화된 에러 응답 |
| Auth Guard | api/deps.py | JWT 검증, 권한 확인 |
| Connection Pool | db/connection.py | DB 커넥션 관리 |
| Retry Pattern | external/order_client.py | 서비스 간 통신 복원력 |
| Health Check | api/routes/health.py | 서비스 상태 모니터링 |
| Structured Logging | middleware/logging.py | 관찰성 |
