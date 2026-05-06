# Application Design Plan

## 개요
테이블오더 서비스의 애플리케이션 컴포넌트 식별 및 서비스 레이어 설계 계획입니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
백엔드 API 구조를 어떻게 구성하시겠습니까?

A) 단일 FastAPI 애플리케이션 (모든 도메인을 라우터로 분리)
B) 도메인별 분리된 마이크로서비스 (주문 서비스, 메뉴 서비스, 인증 서비스 등)
C) 모듈러 모놀리스 (단일 앱이지만 도메인별 모듈로 명확히 분리, 향후 분리 가능)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 2
프론트엔드 프로젝트 구조는 어떻게 하시겠습니까?

A) 단일 React 프로젝트 (고객용/관리자용을 라우팅으로 분리)
B) 2개의 별도 React 프로젝트 (고객용 앱 + 관리자용 앱)
C) 모노레포 (공통 컴포넌트 공유, 고객용/관리자용 별도 빌드)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 3
데이터 접근 레이어는 어떤 패턴을 사용하시겠습니까?

A) SQLAlchemy ORM (모델 정의 + 세션 관리)
B) SQLAlchemy ORM + Repository 패턴 (ORM 위에 추상화 레이어)
C) Raw SQL + 데이터 매퍼 패턴
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 4
컴포넌트 간 통신 패턴은 어떤 것을 선호하십니까?

A) 직접 함수 호출 (서비스 레이어에서 다른 서비스 직접 호출)
B) 이벤트 기반 (내부 이벤트 버스를 통한 느슨한 결합)
C) 혼합 — 동기 작업은 직접 호출, 비동기 작업(SSE 알림 등)은 이벤트 기반
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 5
상태 관리 (프론트엔드)는 어떤 방식을 사용하시겠습니까?

A) React Context + useReducer (가벼운 상태 관리)
B) Zustand (간결한 전역 상태 관리)
C) Redux Toolkit (구조화된 상태 관리, 미들웨어 지원)
D) TanStack Query (서버 상태) + Zustand (클라이언트 상태) 조합
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 실행 단계

답변 승인 후 아래 단계를 순차적으로 실행합니다.

- [x] Step 1: 컴포넌트 식별 및 정의 (components.md)
  - [x] 백엔드 컴포넌트 식별 (도메인별)
  - [x] 프론트엔드 컴포넌트 식별 (화면별)
  - [x] 공통/인프라 컴포넌트 식별

- [x] Step 2: 컴포넌트 메서드 정의 (component-methods.md)
  - [x] 각 백엔드 컴포넌트의 주요 메서드 시그니처
  - [x] 각 프론트엔드 컴포넌트의 주요 인터페이스
  - [x] 입출력 타입 정의

- [x] Step 3: 서비스 레이어 설계 (services.md)
  - [x] 서비스 정의 및 책임 범위
  - [x] 서비스 간 오케스트레이션 패턴
  - [x] 트랜잭션 경계 정의

- [x] Step 4: 컴포넌트 의존성 매핑 (component-dependency.md)
  - [x] 의존성 매트릭스 생성
  - [x] 통신 패턴 정의
  - [x] 데이터 흐름 다이어그램

- [x] Step 5: 통합 문서 생성 (application-design.md)
  - [x] 전체 설계 통합 문서 작성
  - [x] 설계 일관성 검증
