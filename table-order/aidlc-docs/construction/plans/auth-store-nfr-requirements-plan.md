# NFR Requirements Plan — Auth Service + Store Service (개발자 A)

## 개요
Unit 1 (Auth Service)과 Unit 2 (Store Service)의 비기능 요구사항 및 기술 스택 결정입니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
Auth Service의 응답 시간 목표는 어떻게 설정하시겠습니까?

A) 로그인 API: 500ms 이내, 토큰 검증: 50ms 이내
B) 로그인 API: 1초 이내, 토큰 검증: 100ms 이내
C) 특별한 목표 없음 — 합리적인 수준이면 됨
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 2
비밀번호 해싱 라이브러리는 어떤 것을 사용하시겠습니까?

A) bcrypt (passlib 라이브러리)
B) argon2 (argon2-cffi 라이브러리)
C) bcrypt (python-bcrypt 직접 사용)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
DB 마이그레이션 도구는 어떤 것을 사용하시겠습니까?

A) Alembic (SQLAlchemy 기반, Raw SQL도 지원)
B) 직접 SQL 마이그레이션 스크립트 관리
C) dbmate (언어 무관, SQL 파일 기반)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 4
API 문서화 방식은 어떻게 하시겠습니까?

A) FastAPI 내장 Swagger (자동 생성)
B) FastAPI Swagger + 추가 설명/예시 수동 보강
C) 별도 OpenAPI YAML 파일 작성 후 FastAPI에 연동
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 5
로깅 프레임워크는 어떤 것을 사용하시겠습니까?

A) Python 표준 logging + structlog (구조화된 JSON 로깅)
B) loguru (간편한 로깅)
C) Python 표준 logging만 사용
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## 실행 단계

- [x] Step 1: 성능 요구사항 정의
  - [x] 응답 시간 목표
  - [x] 동시 접속 처리 용량

- [x] Step 2: 보안 요구사항 정의
  - [x] 인증/인가 보안 규칙
  - [x] 데이터 보호 규칙
  - [x] Security Baseline 규칙 매핑

- [x] Step 3: 기술 스택 결정
  - [x] 핵심 라이브러리 선정
  - [x] 개발/테스트 도구 선정
  - [x] PBT 프레임워크 확인 (PBT-09)
