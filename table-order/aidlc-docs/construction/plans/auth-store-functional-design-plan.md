# Functional Design Plan — Auth Service + Store Service (개발자 A)

## 개요
Unit 1 (Auth Service)과 Unit 2 (Store Service)의 상세 비즈니스 로직 설계 계획입니다.

---

## 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

### Question 1
JWT 토큰 구조는 어떻게 하시겠습니까?

A) Access Token만 사용 (16시간 만료, 만료 시 재로그인)
B) Access Token (짧은 만료, 예: 1시간) + Refresh Token (16시간 만료)
C) Access Token (16시간) + 토큰 갱신 없이 만료 시 재로그인
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
로그인 시도 제한 정책은 어떻게 하시겠습니까?

A) 5회 실패 시 15분 잠금
B) 5회 실패 시 30분 잠금
C) 점진적 지연 (1회 실패: 즉시, 3회: 30초 대기, 5회: 5분 잠금)
D) 10회 실패 시 계정 잠금 (관리자 해제 필요)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
테이블 세션의 시작 시점은 언제로 정의하시겠습니까?

A) 테이블 태블릿이 로그인하는 시점 (관리자 초기 설정 시)
B) 해당 테이블에서 첫 번째 주문이 생성되는 시점
C) 관리자가 명시적으로 "새 세션 시작" 버튼을 누르는 시점
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 4
테이블 세션 종료(이용 완료) 시 태블릿 동작은 어떻게 되나요?

A) 태블릿은 그대로 메뉴 화면 유지 (새 고객이 바로 주문 가능, 새 세션은 첫 주문 시 자동 시작)
B) 태블릿에 "이용 완료" 화면 표시 후 일정 시간 뒤 메뉴 화면으로 복귀
C) 태블릿 자동 로그아웃 (관리자가 다시 설정해야 함)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 5
매장(Store) 초기 데이터 생성은 어떻게 하시겠습니까?

A) API를 통한 매장 등록 (별도 슈퍼 관리자 또는 시드 스크립트)
B) DB 시드 스크립트로 초기 매장 데이터 삽입
C) 첫 관리자 로그인 시 매장 자동 생성 (셀프 서비스 등록)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 실행 단계

- [x] Step 1: Auth Service 도메인 엔티티 설계
  - [x] Admin 엔티티 (관리자 계정)
  - [x] TableCredential 엔티티 (테이블 인증 정보)
  - [x] LoginAttempt 엔티티 (로그인 시도 기록)
  - [x] Token 구조 (JWT payload)

- [x] Step 2: Auth Service 비즈니스 규칙 정의
  - [x] 관리자 인증 규칙
  - [x] 테이블 인증 규칙
  - [x] 토큰 발급/검증 규칙
  - [x] 로그인 시도 제한 규칙

- [x] Step 3: Store Service 도메인 엔티티 설계
  - [x] Store 엔티티 (매장)
  - [x] Table 엔티티 (테이블)
  - [x] TableSession 엔티티 (테이블 세션)

- [x] Step 4: Store Service 비즈니스 규칙 정의
  - [x] 테이블 관리 규칙
  - [x] 세션 라이프사이클 규칙
  - [x] 이용 완료 처리 규칙

- [x] Step 5: 비즈니스 로직 모델 통합
  - [x] Auth ↔ Store 연동 로직
  - [x] 에러 시나리오 정의
