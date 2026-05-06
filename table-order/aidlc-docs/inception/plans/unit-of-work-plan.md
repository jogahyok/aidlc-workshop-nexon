# Unit of Work Plan

## 개요
테이블오더 서비스를 개발 가능한 작업 단위(Unit of Work)로 분해하는 계획입니다.
Application Design에서 정의된 마이크로서비스 구조를 기반으로 합니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
유닛(서비스) 개발 순서는 어떻게 하시겠습니까?

A) 의존성 순서 — 의존받는 서비스부터 (Auth → Store → Menu → Order → Frontend)
B) 비즈니스 가치 순서 — 핵심 기능부터 (Order → Menu → Store → Auth → Frontend)
C) 프론트엔드 우선 — UI 먼저 만들고 백엔드 연동 (Frontend → Backend 서비스들)
D) 병렬 개발 — 모든 서비스 동시 개발 (API 계약 먼저 정의 후 병렬)
X) Other (please describe after [Answer]: tag below)

[Answer]: D

### Question 2
프론트엔드를 별도 유닛으로 분리하시겠습니까?

A) 프론트엔드 전체를 1개 유닛으로 (Customer App + Admin App + Shared UI)
B) 고객용과 관리자용을 별도 유닛으로 (Customer Unit + Admin Unit)
C) 백엔드 서비스와 함께 묶기 (각 백엔드 유닛에 관련 프론트엔드 포함)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
공통 인프라(DB 스키마, API Gateway, 공통 라이브러리)는 어떻게 처리하시겠습니까?

A) 별도 "인프라/공통" 유닛으로 분리하여 먼저 구축
B) 각 서비스 유닛에 필요한 인프라를 포함 (서비스별 자체 스키마 마이그레이션)
C) 첫 번째 서비스 유닛에 공통 인프라 포함, 이후 서비스는 재사용
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 4
각 유닛의 완료 기준은 무엇으로 하시겠습니까?

A) API 구현 완료 + 단위 테스트 통과
B) API 구현 + 단위 테스트 + 통합 테스트 통과
C) API 구현 + 테스트 + API 문서(Swagger) 완성
D) API 구현 + 테스트 + 문서 + 프론트엔드 연동 확인
X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## 실행 단계

답변 승인 후 아래 단계를 순차적으로 실행합니다.

- [x] Step 1: 유닛 정의 (unit-of-work.md)
  - [x] 각 유닛의 범위, 책임, 포함 컴포넌트 정의
  - [x] 유닛별 코드 조직 전략 문서화
  - [x] 유닛별 완료 기준 명시

- [x] Step 2: 유닛 의존성 매핑 (unit-of-work-dependency.md)
  - [x] 유닛 간 의존성 매트릭스 생성
  - [x] 개발 순서 및 병렬화 가능 여부 정의
  - [x] 통합 포인트 식별

- [x] Step 3: 스토리-유닛 매핑 (unit-of-work-story-map.md)
  - [x] 각 사용자 스토리를 담당 유닛에 할당
  - [x] 크로스-유닛 스토리 식별 및 분할 전략
  - [x] 매핑 완전성 검증 (모든 스토리 할당 확인)
