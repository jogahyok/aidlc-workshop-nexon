# NFR Design Plan — Frontend (개발자 C)

## 개요
Unit 5 (Frontend)의 NFR 요구사항을 실제 설계 패턴과 논리적 컴포넌트로 구체화하는 계획입니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
API 호출 실패 시 재시도 전략은 어떻게 하시겠습니까?

A) 모든 GET 요청 자동 재시도 3회 (지수 백오프), POST/PATCH/DELETE는 재시도 안 함
B) 모든 요청 자동 재시도 3회 (멱등성 관계없이)
C) 재시도 없음 — 실패 시 사용자에게 수동 재시도 버튼 제공
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
프론트엔드 에러 바운더리 범위는 어떻게 설정하시겠습니까?

A) 페이지 레벨 — 페이지 단위로 에러 격리 (한 페이지 에러가 다른 페이지에 영향 없음)
B) 컴포넌트 레벨 — 주요 섹션별 에러 격리 (대시보드 내 개별 카드 에러 격리)
C) 앱 레벨 — 전체 앱에 하나의 에러 바운더리 (에러 시 전체 fallback)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
API 응답 캐싱 전략은 어떻게 하시겠습니까?

A) 적극적 캐싱 — 메뉴 데이터 10분, 주문 데이터 1분 캐시
B) 보통 캐싱 — 메뉴 데이터 5분, 주문 데이터 30초 캐시
C) 최소 캐싱 — 메뉴 데이터 1분, 주문 데이터는 항상 fresh
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## 실행 단계

- [x] Step 1: 성능 패턴 설계
  - [x] 코드 스플리팅 전략 (React.lazy + Suspense)
  - [x] 이미지 최적화 패턴 (lazy loading, placeholder)
  - [x] 캐싱 전략 (TanStack Query staleTime/cacheTime)
  - [x] 렌더링 최적화 (React.memo, useMemo, useCallback)

- [x] Step 2: 복원력 패턴 설계
  - [x] 에러 바운더리 계층 구조
  - [x] API 재시도 패턴 (TanStack Query retry)
  - [x] SSE 재연결 패턴
  - [x] 네트워크 상태 감지 패턴

- [x] Step 3: 보안 패턴 설계
  - [x] 인증 인터셉터 패턴 (Axios)
  - [x] 토큰 갱신/만료 처리 패턴
  - [x] 입력 검증 패턴 (Zod 스키마)
  - [x] XSS 방지 패턴

- [x] Step 4: 논리적 컴포넌트 정의
  - [x] API Client Layer (Axios 인스턴스 + 인터셉터)
  - [x] Auth Guard (라우트 보호)
  - [x] Error Reporter (에러 수집/전송)
  - [x] SSE Manager (연결 관리)
  - [x] Storage Manager (localStorage 래퍼)
