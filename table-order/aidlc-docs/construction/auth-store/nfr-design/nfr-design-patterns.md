# NFR Design Patterns — Auth Service + Store Service

## 1. 보안 패턴

### 1.1 인증 미들웨어 구조
```
Request → [CORS] → [Request ID] → [Rate Limit] → [Auth Guard] → Handler → Response
                                                        |
                                                   [Token Verify]
                                                        |
                                                   JWT Decode → Payload
```

**Auth Guard 미들웨어:**
- FastAPI `Depends()` 기반 의존성 주입
- 공개 엔드포인트: 데코레이터로 인증 제외 표시
- 보호 엔드포인트: `get_current_user` 의존성 자동 주입
- 관리자 전용: `get_current_admin` (type='admin' 검증 추가)
- 매장 격리: `verify_store_access` (토큰의 store_id와 요청 store_id 일치 확인)

```python
# 패턴 예시
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """모든 보호 엔드포인트에 주입"""
    
async def get_current_admin(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """관리자 전용 엔드포인트에 주입 (type='admin' 검증)"""

async def verify_store_access(store_id: int, user: TokenPayload = Depends(get_current_user)):
    """매장 격리 검증 (IDOR 방지)"""
```

### 1.2 Rate Limiting 패턴
- **구현**: 인메모리 딕셔너리 기반 (단일 인스턴스 기준)
- **키**: `{store_id}:{identifier}:{attempt_type}`
- **윈도우**: 슬라이딩 윈도우 15분
- **임계값**: 5회 실패
- **저장소**: LoginAttempt 테이블 (영속적 기록) + 인메모리 캐시 (빠른 판단)

```python
# 패턴: 잠금 확인 → DB 조회 (최근 15분 실패 횟수)
async def is_locked(store_id: int, identifier: str, attempt_type: str) -> bool:
    count = await count_recent_failures(store_id, identifier, attempt_type, minutes=15)
    return count >= 5
```

### 1.3 에러 응답 표준화 패턴
```json
{
  "error": {
    "code": "AUTH_002",
    "message": "인증 정보가 올바르지 않습니다",
    "details": null
  },
  "request_id": "uuid-here"
}
```

**글로벌 예외 핸들러:**
- `AppException` (커스텀 비즈니스 예외) → 정의된 HTTP 코드 + 에러 코드
- `ValidationError` (Pydantic) → 422 + 필드별 에러 상세
- `Exception` (미처리) → 500 + 일반 메시지 (내부 정보 노출 금지)

---

## 2. 복원력 패턴

### 2.1 서비스 간 통신 재시도 패턴
- **대상**: Store Service → Order Service (세션 종료 시 아카이브)
- **전략**: 단순 재시도, 최대 3회, 1초 간격
- **타임아웃**: 개별 요청 5초, 전체 작업 20초

```python
# 패턴: httpx 기반 재시도
async def call_with_retry(url: str, payload: dict, max_retries: int = 3) -> Response:
    for attempt in range(max_retries):
        try:
            response = await client.post(url, json=payload, timeout=5.0)
            response.raise_for_status()
            return response
        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            if attempt == max_retries - 1:
                raise ServiceUnavailableError(f"Service call failed after {max_retries} attempts")
            await asyncio.sleep(1.0)
```

**실패 처리:**
- 3회 재시도 모두 실패 → STORE_005 에러 반환
- 세션 종료 작업 롤백 (세션 상태 변경하지 않음)
- 에러 로깅 (request_id, 대상 서비스, 실패 원인)

### 2.2 DB 커넥션 풀 관리 패턴
- **라이브러리**: aiomysql.Pool
- **설정**: 자동 조절 (min: 1, max: 동적)
- **동적 확장 전략**:
  - 초기: minsize=1, maxsize=10
  - 부하 증가 시 자동 확장 (aiomysql 내장)
  - 유휴 커넥션 자동 회수 (pool_recycle=3600)
- **연결 끊김 처리**: 자동 재연결 (echo=True로 연결 상태 확인)

```python
# 패턴: 앱 시작/종료 시 풀 관리
pool = await aiomysql.create_pool(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    db=settings.db_name,
    minsize=1,
    maxsize=10,
    pool_recycle=3600,
    autocommit=True,
)
```

### 2.3 헬스체크 패턴
```python
# GET /health
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "checks": {
            "database": "ok" if db_ok else "failed"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 3. 관찰성 패턴

### 3.1 요청 ID 전파
- **생성**: 미들웨어에서 UUID4 생성 (X-Request-ID 헤더 없으면)
- **전파**: 서비스 간 HTTP 호출 시 X-Request-ID 헤더 포함
- **로깅**: 모든 로그에 request_id 포함

```python
# 미들웨어 패턴
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    # contextvars로 전파
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 3.2 구조화된 로깅 패턴
```python
# JSON 로그 포맷 (production)
{
    "timestamp": "2026-05-06T12:00:00Z",
    "level": "INFO",
    "request_id": "uuid-here",
    "message": "Admin login successful",
    "store_id": 1,
    "username": "admin"  # 민감 정보 제외
}
```

**로깅 규칙:**
- 절대 로깅 금지: password, token, password_hash
- 마스킹 처리: IP 주소 (마지막 옥텟 마스킹 선택)
- 필수 포함: timestamp, level, request_id, message
