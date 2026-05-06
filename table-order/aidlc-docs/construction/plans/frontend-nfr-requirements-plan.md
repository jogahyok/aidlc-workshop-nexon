# NFR Requirements Plan — Frontend (개발자 C)

## 개요
Unit 5 (Frontend)의 비기능 요구사항 평가 및 기술 스택 세부 결정 계획입니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
프론트엔드 번들 크기 목표는 어떻게 설정하시겠습니까?

A) 엄격 — 초기 로드 200KB 이하 (코드 스플리팅 적극 활용)
B) 보통 — 초기 로드 500KB 이하 (주요 페이지별 코드 스플리팅)
C) 관대 — 크기 제한 없음 (내부 네트워크 태블릿 사용이므로 성능 우선순위 낮음)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 2
테스트 커버리지 목표는 어떻게 설정하시겠습니까?

A) 높음 — 80% 이상 (비즈니스 로직 + 컴포넌트 + 통합 테스트)
B) 중간 — 60% 이상 (비즈니스 로직 + 핵심 컴포넌트)
C) 핵심만 — 비즈니스 로직(장바구니 계산, 인증)만 테스트
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 3
브라우저 호환성 범위는 어떻게 하시겠습니까?

A) 최신 브라우저만 (Chrome/Edge 최신 2버전) — 태블릿 전용이므로
B) 모던 브라우저 (Chrome, Firefox, Safari, Edge 최신 2버전)
C) 넓은 호환성 (IE11 제외, 2년 이내 브라우저 모두)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 4
에러 모니터링 및 로깅은 어떻게 하시겠습니까?

A) 외부 서비스 사용 (Sentry 등 — 실시간 에러 추적, 소스맵 지원)
B) 콘솔 로깅 + 서버 전송 (커스텀 에러 리포팅 API)
C) 콘솔 로깅만 (개발 단계에서는 충분)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## 실행 단계

- [x] Step 1: 성능 요구사항 정의
  - [x] 페이지 로드 시간 목표
  - [x] 번들 크기 제한
  - [x] 렌더링 성능 기준

- [x] Step 2: 보안 요구사항 정의 (Security Baseline 준수)
  - [x] XSS 방지 전략
  - [x] CSRF 보호
  - [x] 토큰 보안 저장
  - [x] CSP 정책 정의
  - [x] HTTP 보안 헤더

- [x] Step 3: 테스트 전략 정의 (PBT 포함)
  - [x] 단위 테스트 범위
  - [x] PBT 대상 식별 (장바구니 계산, 가격 invariant)
  - [x] 통합 테스트 범위
  - [x] 테스트 프레임워크 확정

- [x] Step 4: 가용성 및 에러 복구 정의
  - [x] 오프라인 대응 전략
  - [x] 에러 바운더리 설계
  - [x] 재시도 정책

- [x] Step 5: 기술 스택 세부 결정
  - [x] 의존성 버전 확정
  - [x] 개발 도구 (ESLint, Prettier, Husky)
  - [x] CI/CD 파이프라인 고려사항
