# 요구사항 확인 질문

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.
제공된 옵션 중 맞는 것이 없으면 마지막 옵션(Other)을 선택하고 설명을 추가해 주세요.

---

## Question 1
백엔드 기술 스택으로 어떤 것을 사용하시겠습니까?

A) Node.js + Express (JavaScript/TypeScript)
B) Node.js + NestJS (TypeScript)
C) Spring Boot (Java/Kotlin)
D) Python + FastAPI
X) Other (please describe after [Answer]: tag below)

[Answer]: D

## Question 2
프론트엔드 기술 스택으로 어떤 것을 사용하시겠습니까?

A) React (TypeScript)
B) Vue.js (TypeScript)
C) Next.js (React 기반 풀스택 프레임워크)
D) Vanilla HTML/CSS/JavaScript
X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3
데이터베이스로 어떤 것을 사용하시겠습니까?

A) PostgreSQL
B) MySQL
C) MongoDB
D) SQLite (개발/소규모 매장용)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 4
이 서비스의 배포 환경은 어떻게 계획하고 계십니까?

A) AWS 클라우드 (EC2, RDS, etc.)
B) Docker 컨테이너 기반 (로컬 또는 클라우드)
C) 로컬 서버 (온프레미스)
D) 배포 환경은 아직 미정 — 로컬 개발 환경만 우선 구성
X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5
매장(Store) 관리 구조는 어떻게 되나요? (멀티테넌시)

A) 단일 매장만 지원 (1개 매장 전용 시스템)
B) 다중 매장 지원 (여러 매장이 하나의 시스템 공유, 각 매장 독립 데이터)
C) 아직 미정 — 우선 단일 매장으로 시작하되 확장 가능한 구조
X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 6
메뉴 이미지 관리는 어떻게 처리하시겠습니까?

A) 외부 이미지 URL 직접 입력 (별도 업로드 없음)
B) 서버에 이미지 파일 업로드 (로컬 파일 시스템 저장)
C) 클라우드 스토리지 업로드 (S3, GCS 등)
D) 이미지 기능은 MVP에서 제외 (텍스트만 표시)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 7
고객용 인터페이스의 접근 방식은 어떻게 되나요?

A) 태블릿 전용 웹앱 (고정 URL 접속, 브라우저 전체화면)
B) QR코드 스캔으로 모바일 브라우저 접속
C) 태블릿 전용 + QR코드 모바일 접속 모두 지원
X) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 8
동시 접속 규모는 어느 정도로 예상하십니까?

A) 소규모 (1개 매장, 테이블 10개 이하)
B) 중규모 (1개 매장, 테이블 10~50개)
C) 대규모 (다중 매장, 총 테이블 100개 이상)
D) 규모는 미정 — 소규모로 시작
X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 9
관리자 계정 관리는 어떻게 하시겠습니까?

A) 매장당 1개의 관리자 계정 (단일 관리자)
B) 매장당 여러 관리자 계정 (역할 구분 없음)
C) 매장당 여러 관리자 계정 (역할별 권한 구분: 점주, 매니저 등)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 10
메뉴 옵션/추가 선택 기능이 필요합니까? (예: 사이즈 선택, 토핑 추가, 맵기 조절 등)

A) 필요 없음 — 메뉴 항목만 선택하고 수량만 조절
B) 기본 옵션만 지원 (예: 사이즈 S/M/L)
C) 복합 옵션 지원 (사이즈 + 토핑 + 기타 커스터마이징)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 11: Security Extensions
이 프로젝트에 보안 확장 규칙을 적용하시겠습니까?

A) Yes — 모든 보안 규칙을 필수 제약으로 적용 (프로덕션 수준 애플리케이션에 권장)
B) No — 보안 규칙 건너뛰기 (PoC, 프로토타입, 실험적 프로젝트에 적합)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 12: Property-Based Testing Extension
이 프로젝트에 속성 기반 테스팅(PBT) 규칙을 적용하시겠습니까?

A) Yes — 모든 PBT 규칙을 필수 제약으로 적용 (비즈니스 로직, 데이터 변환, 직렬화, 상태 관리 컴포넌트가 있는 프로젝트에 권장)
B) Partial — 순수 함수와 직렬화 라운드트립에만 PBT 규칙 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)
C) No — 모든 PBT 규칙 건너뛰기 (단순 CRUD 애플리케이션, UI 전용 프로젝트에 적합)
X) Other (please describe after [Answer]: tag below)

[Answer]: A
