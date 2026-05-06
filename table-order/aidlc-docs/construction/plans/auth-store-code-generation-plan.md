# Code Generation Plan — Auth Service + Store Service (개발자 A)

## Unit Context
- **유닛**: Unit 1 (Auth Service) + Unit 2 (Store Service)
- **담당**: 개발자 A
- **스토리**: US-01 (테이블 자동 로그인), US-07 (관리자 인증), US-09 (테이블 관리)
- **의존성**: Order Service (세션 종료 시 아카이브 HTTP 호출)
- **코드 위치**: `services/auth-service/`, `services/store-service/`

## 기술 스택
- Python 3.11+ / FastAPI / uvicorn
- aiomysql (비동기 MySQL)
- passlib[bcrypt] / python-jose (JWT)
- dbmate (마이그레이션)
- pytest + hypothesis (테스트)

---

## 코드 생성 단계

### Auth Service

- [ ] Step 1: Auth Service 프로젝트 구조 생성
  - `services/auth-service/` 디렉토리 구조
  - requirements.txt (pinned versions)
  - Dockerfile
  - .env.example
  - dbmate 설정

- [ ] Step 2: Auth Service 핵심 모듈 생성
  - `app/core/config.py` — Pydantic Settings
  - `app/core/security.py` — JWT 생성/검증, bcrypt 해싱
  - `app/core/exceptions.py` — 커스텀 예외 클래스

- [ ] Step 3: Auth Service DB 레이어 생성
  - `app/db/connection.py` — 커넥션 풀 관리
  - `app/db/queries/admin_queries.py` — Admin Raw SQL 쿼리
  - `app/db/queries/table_credential_queries.py` — TableCredential 쿼리
  - `app/db/queries/login_attempt_queries.py` — LoginAttempt 쿼리
  - `app/db/mappers/` — 쿼리 결과 → 도메인 모델 매핑

- [ ] Step 4: Auth Service 도메인 모델 및 스키마 생성
  - `app/models/` — Admin, TableCredential, LoginAttempt 도메인 모델
  - `app/schemas/auth.py` — 요청/응답 Pydantic 스키마
  - `app/schemas/common.py` — 공통 에러 응답 스키마

- [ ] Step 5: Auth Service 비즈니스 로직 생성
  - `app/services/auth_service.py` — 관리자/테이블 인증 로직
  - `app/services/login_attempt_service.py` — 잠금 판단 로직

- [ ] Step 6: Auth Service API 라우트 생성
  - `app/api/deps.py` — 공통 의존성 (get_db, get_current_user)
  - `app/api/routes/auth.py` — 로그인/토큰 엔드포인트
  - `app/api/routes/health.py` — 헬스체크

- [ ] Step 7: Auth Service 미들웨어 및 메인 앱 생성
  - `app/middleware/request_id.py` — Request ID 미들웨어
  - `app/middleware/logging_middleware.py` — 로깅 미들웨어
  - `app/main.py` — FastAPI 앱 초기화, 미들웨어/라우터 등록

- [ ] Step 8: Auth Service DB 마이그레이션 생성
  - `migrations/001_create_auth_tables.sql` — admins, table_credentials, login_attempts 테이블

- [ ] Step 9: Auth Service 단위 테스트 생성
  - `tests/conftest.py` — 테스트 설정, 픽스처
  - `tests/test_security.py` — JWT round-trip PBT, bcrypt 검증
  - `tests/test_auth_service.py` — 인증 로직 테스트
  - `tests/test_login_attempts.py` — 잠금 invariant PBT

---

### Store Service

- [ ] Step 10: Store Service 프로젝트 구조 생성
  - `services/store-service/` 디렉토리 구조
  - requirements.txt, Dockerfile, .env.example

- [ ] Step 11: Store Service 핵심 모듈 생성
  - `app/core/config.py` — Settings
  - `app/core/exceptions.py` — 커스텀 예외

- [ ] Step 12: Store Service DB 레이어 생성
  - `app/db/connection.py` — 커넥션 풀
  - `app/db/queries/store_queries.py` — Store 쿼리
  - `app/db/queries/table_queries.py` — Table 쿼리
  - `app/db/queries/session_queries.py` — TableSession 쿼리
  - `app/db/mappers/` — 데이터 매퍼

- [ ] Step 13: Store Service 도메인 모델 및 스키마 생성
  - `app/models/` — Store, Table, TableSession 모델
  - `app/schemas/` — 요청/응답 스키마

- [ ] Step 14: Store Service 비즈니스 로직 생성
  - `app/services/store_service.py` — 매장 관리
  - `app/services/table_service.py` — 테이블 CRUD
  - `app/services/session_service.py` — 세션 라이프사이클

- [ ] Step 15: Store Service 외부 클라이언트 생성
  - `app/external/order_client.py` — Order Service HTTP 클라이언트 (재시도 포함)

- [ ] Step 16: Store Service API 라우트 생성
  - `app/api/deps.py` — 공통 의존성
  - `app/api/routes/stores.py` — 매장 관리 엔드포인트
  - `app/api/routes/tables.py` — 테이블 관리 엔드포인트
  - `app/api/routes/sessions.py` — 세션 관리 엔드포인트
  - `app/api/routes/health.py` — 헬스체크

- [ ] Step 17: Store Service 미들웨어 및 메인 앱 생성
  - `app/middleware/` — Request ID, 로깅
  - `app/main.py` — FastAPI 앱

- [ ] Step 18: Store Service DB 마이그레이션 생성
  - `migrations/001_create_store_tables.sql` — stores, tables, table_sessions 테이블

- [ ] Step 19: Store Service 단위 테스트 생성
  - `tests/conftest.py` — 테스트 설정
  - `tests/test_session_service.py` — 세션 상태 머신 PBT
  - `tests/test_table_service.py` — 테이블 관리 테스트
  - `tests/test_order_client.py` — 재시도 로직 테스트

---

### 공통

- [ ] Step 20: Docker Compose 및 배포 설정 생성
  - `docker-compose.yml` — 전체 서비스 구성 (개발용)
  - `docker-compose.prod.yml` — 프로덕션 구성

---

## 스토리 매핑

| Step | 관련 스토리 |
|------|------------|
| Step 2-9 | US-01 (테이블 인증), US-07 (관리자 인증) |
| Step 10-19 | US-01 (세션 시작), US-09 (테이블 관리, 세션 종료) |
| Step 20 | 전체 배포 |
