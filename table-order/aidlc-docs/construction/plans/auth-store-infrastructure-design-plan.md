# Infrastructure Design Plan — Auth Service + Store Service (개발자 A)

## 개요
Auth Service와 Store Service의 논리적 컴포넌트를 AWS 인프라에 매핑하는 계획입니다.

---

## 질문

### Question 1
컴퓨팅 서비스는 어떤 것을 사용하시겠습니까?

A) EC2 인스턴스 (Docker Compose로 서비스 배포)
B) ECS Fargate (서버리스 컨테이너)
C) ECS EC2 (자체 관리 컨테이너 클러스터)
D) 개발 단계에서는 EC2 단일 인스턴스, 프로덕션에서 ECS 전환
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2
RDS MySQL 인스턴스 구성은 어떻게 하시겠습니까?

A) 단일 인스턴스 (db.t3.micro, 개발/소규모)
B) 단일 인스턴스 (db.t3.small, 중규모)
C) Multi-AZ (고가용성, 프로덕션)
D) 개발: db.t3.micro, 프로덕션: db.t3.small + Multi-AZ
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 3
네트워크 구성은 어떻게 하시겠습니까?

A) 기본 VPC 사용 (간단한 구성)
B) 커스텀 VPC (Public/Private 서브넷 분리, NAT Gateway)
C) 개발: 기본 VPC, 프로덕션: 커스텀 VPC
X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## 실행 단계

- [x] Step 1: 컴퓨팅 인프라 설계
  - [x] 서비스 배포 방식
  - [x] 스케일링 전략
  - [x] 컨테이너 구성

- [x] Step 2: 데이터 인프라 설계
  - [x] RDS 구성
  - [x] 보안 그룹 설정
  - [x] 백업 전략

- [x] Step 3: 네트워크 인프라 설계
  - [x] VPC/서브넷 구성
  - [x] 로드 밸런서 설정
  - [x] 보안 그룹 규칙
