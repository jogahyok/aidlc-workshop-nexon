# Tech Stack Decisions — Auth Service + Store Service

## 핵심 런타임

| 카테고리 | 기술 | 버전 | 근거 |
|----------|------|------|------|
| 언어 | Python | 3.11+ | FastAPI 호환, 최신 기능 |
| 프레임워크 | FastAPI | 0.104+ | 비동기 지원, 자동 문서화, Pydantic 통합 |
| ASGI 서버 | uvicorn | 0.24+ | FastAPI 표준 서버 |
| DB 드라이버 | aiomysql | 0.2+ | 비동기 MySQL 드라이버 |

## 핵심 라이브러리

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| pydantic | 입력 검증, 스키마 정의 | 2.5+ |
| passlib[bcrypt] | 비밀번호 해싱 (bcrypt) | 1.7+ |
| python-jose[cryptography] | JWT 토큰 생성/검증 | 3.3+ |
| httpx | 서비스 간 HTTP 통신 (비동기) | 0.25+ |

## 데이터베이스

| 카테고리 | 기술 | 비고 |
|----------|------|------|
| RDBMS | MySQL 8.0 | AWS RDS |
| 커넥션 풀 | aiomysql Pool | 비동기 커넥션 풀 |
| 마이그레이션 | dbmate | SQL 파일 기반, 언어 무관 |

## 개발/테스트 도구

| 도구 | 용도 | 버전 |
|------|------|------|
| pytest | 테스트 프레임워크 | 7.4+ |
| pytest-asyncio | 비동기 테스트 지원 | 0.23+ |
| hypothesis | Property-Based Testing (PBT-09) | 6.92+ |
| httpx (TestClient) | API 통합 테스트 | - |
| ruff | 린터 + 포매터 | 0.1+ |
| mypy | 타입 체크 | 1.7+ |

## 로깅

| 카테고리 | 기술 | 비고 |
|----------|------|------|
| 프레임워크 | Python 표준 logging | 추가 의존성 없음 |
| 포맷 | JSON (production), 텍스트 (development) | 환경별 설정 |
| 필수 필드 | timestamp, request_id, level, message | SECURITY-03 준수 |

## API 문서화

| 카테고리 | 기술 | 비고 |
|----------|------|------|
| 문서 생성 | FastAPI 내장 Swagger UI | 자동 생성 |
| 스키마 | Pydantic 모델 기반 자동 생성 | OpenAPI 3.0 |
| 접근 경로 | /docs (Swagger), /redoc (ReDoc) | 기본 제공 |

## 컨테이너화

| 카테고리 | 기술 | 비고 |
|----------|------|------|
| 컨테이너 | Docker | 멀티스테이지 빌드 |
| 베이스 이미지 | python:3.11-slim | 경량 이미지 |
| 의존성 관리 | requirements.txt (pinned versions) | SECURITY-10 준수 |

## PBT 프레임워크 (PBT-09 준수)

| 항목 | 내용 |
|------|------|
| 프레임워크 | Hypothesis |
| 커스텀 생성기 | 지원 (st.composite) |
| 자동 축소 | 지원 (내장) |
| 시드 재현 | 지원 (--hypothesis-seed) |
| 테스트 러너 통합 | pytest 통합 |

## 의존성 요약 (requirements.txt)

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.2
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
aiomysql==0.2.0
httpx==0.25.2
python-multipart==0.0.6

# Dev/Test
pytest==7.4.3
pytest-asyncio==0.23.2
hypothesis==6.92.1
ruff==0.1.8
mypy==1.7.1
```
