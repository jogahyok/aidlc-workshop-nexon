# NFR Design Plan — Auth Service + Store Service (개발자 A)

## 개요
NFR 요구사항을 실제 설계 패턴과 논리적 컴포넌트로 반영하는 계획입니다.

---

## 질문

### Question 1
서비스 간 HTTP 통신(Store → Order) 실패 시 재시도 전략은 어떻게 하시겠습니까?

A) 단순 재시도 (최대 3회, 1초 간격)
B) 지수 백오프 재시도 (최대 3회, 1s → 2s → 4s)
C) 재시도 없음 — 즉시 실패 반환 (클라이언트가 재시도 판단)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
DB 커넥션 풀 설정은 어떻게 하시겠습니까?

A) 소규모 (min: 2, max: 10) — 단일 매장 기준
B) 중규모 (min: 5, max: 20) — 다중 매장 기준
C) 자동 조절 — 부하에 따라 동적 확장
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 3
요청 ID(Correlation ID) 전파 방식은 어떻게 하시겠습니까?

A) 미들웨어에서 UUID 생성, X-Request-ID 헤더로 서비스 간 전파
B) 클라이언트가 생성한 ID를 그대로 사용
C) 요청 ID 없이 타임스탬프 기반 로그만 사용
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 실행 단계

- [x] Step 1: 보안 패턴 설계
  - [x] 인증 미들웨어 구조
  - [x] Rate Limiting 구현 패턴
  - [x] 에러 응답 표준화 패턴

- [x] Step 2: 복원력 패턴 설계
  - [x] 서비스 간 통신 재시도 패턴
  - [x] DB 커넥션 관리 패턴
  - [x] 헬스체크 패턴

- [x] Step 3: 논리적 컴포넌트 설계
  - [x] 미들웨어 스택 구성
  - [x] 의존성 주입 패턴
  - [x] 설정 관리 패턴
