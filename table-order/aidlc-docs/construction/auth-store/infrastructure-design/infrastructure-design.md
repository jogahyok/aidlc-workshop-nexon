# Infrastructure Design — Auth Service + Store Service

## 인프라 개요

| 항목 | 선택 | 비고 |
|------|------|------|
| 컴퓨팅 | EC2 + Docker Compose | 단일 인스턴스에 모든 서비스 배포 |
| 데이터베이스 | RDS MySQL db.t3.micro | 단일 인스턴스, 서비스별 스키마 분리 |
| 네트워크 | 커스텀 VPC | Public/Private 서브넷, NAT Gateway |
| 로드 밸런서 | ALB | SSL 종료, 경로 기반 라우팅 |
| 스토리지 | S3 | 메뉴 이미지 (Menu Service용, 공유) |

---

## 1. 컴퓨팅 인프라

### EC2 인스턴스
| 항목 | 값 |
|------|-----|
| 인스턴스 타입 | t3.small (2 vCPU, 2GB RAM) |
| AMI | Amazon Linux 2023 |
| 스토리지 | EBS gp3 30GB |
| 서브넷 | Private Subnet |
| 보안 그룹 | sg-app (ALB에서만 접근 허용) |

### Docker Compose 구성
```yaml
# EC2 인스턴스 내 Docker Compose
services:
  auth-service:
    image: auth-service:latest
    ports: ["8001:8000"]
    environment:
      - DB_HOST=<rds-endpoint>
      - JWT_SECRET_KEY=<secret>
    restart: always

  store-service:
    image: store-service:latest
    ports: ["8002:8000"]
    environment:
      - DB_HOST=<rds-endpoint>
      - ORDER_SERVICE_URL=http://order-service:8000
    restart: always

  menu-service:
    image: menu-service:latest
    ports: ["8003:8000"]
    restart: always

  order-service:
    image: order-service:latest
    ports: ["8004:8000"]
    restart: always
```

### 스케일링 전략
- 현재: 단일 EC2 인스턴스 (수직 스케일링)
- 향후: 인스턴스 타입 업그레이드 (t3.small → t3.medium → t3.large)
- 장기: ECS Fargate 전환 시 수평 스케일링

---

## 2. 데이터 인프라

### RDS MySQL
| 항목 | 값 |
|------|-----|
| 엔진 | MySQL 8.0 |
| 인스턴스 클래스 | db.t3.micro (1 vCPU, 1GB RAM) |
| 스토리지 | gp3 20GB (자동 확장 활성화, 최대 100GB) |
| Multi-AZ | No (비용 절감) |
| 서브넷 | Private Subnet (DB Subnet Group) |
| 보안 그룹 | sg-db (EC2에서만 3306 접근) |
| 암호화 | 저장 시 암호화 활성화 (AWS 관리 키) |
| 백업 | 자동 백업 7일 보존 |
| 파라미터 | character_set_server=utf8mb4, require_secure_transport=ON |

### 스키마 분리
```sql
-- 서비스별 논리적 스키마 (단일 RDS 인스턴스)
CREATE DATABASE auth_db;    -- Auth Service 전용
CREATE DATABASE store_db;   -- Store Service 전용
CREATE DATABASE menu_db;    -- Menu Service 전용
CREATE DATABASE order_db;   -- Order Service 전용
```

### 보안
- TLS 1.2+ 강제 (require_secure_transport=ON) — SECURITY-01
- 암호화 at rest (AWS KMS) — SECURITY-01
- 접근: Private Subnet + Security Group 제한 — SECURITY-07

---

## 3. 네트워크 인프라

### VPC 구성
```
VPC: 10.0.0.0/16
├── Public Subnet A:  10.0.1.0/24  (AZ-a) — ALB, NAT Gateway
├── Public Subnet B:  10.0.2.0/24  (AZ-b) — ALB (Multi-AZ)
├── Private Subnet A: 10.0.10.0/24 (AZ-a) — EC2, RDS
└── Private Subnet B: 10.0.11.0/24 (AZ-b) — RDS (Subnet Group)
```

### 보안 그룹

| 보안 그룹 | 인바운드 | 아웃바운드 |
|-----------|----------|-----------|
| sg-alb | 0.0.0.0/0:443 (HTTPS) | sg-app:8001-8004 |
| sg-app | sg-alb:8001-8004 | sg-db:3306, 0.0.0.0/0:443 (NAT) |
| sg-db | sg-app:3306 | 없음 |

### ALB (Application Load Balancer)
| 항목 | 값 |
|------|-----|
| 스킴 | Internet-facing |
| 서브넷 | Public Subnet A, B |
| 리스너 | HTTPS:443 (ACM 인증서) |
| 액세스 로그 | S3 버킷 활성화 — SECURITY-02 |

### 경로 기반 라우팅
| 경로 패턴 | 대상 그룹 | 포트 |
|-----------|-----------|------|
| /api/auth/* | auth-service | 8001 |
| /api/stores/* | store-service | 8002 |
| /api/menus/* | menu-service | 8003 |
| /api/orders/* | order-service | 8004 |
| /* (기본) | frontend (S3/CloudFront) | - |

---

## 4. Security Baseline 인프라 매핑

| SECURITY 규칙 | 인프라 구현 |
|---------------|------------|
| SECURITY-01 | RDS 암호화 at rest + TLS 강제, ALB HTTPS |
| SECURITY-02 | ALB 액세스 로그 → S3 |
| SECURITY-07 | 커스텀 VPC, Private Subnet, Security Group 최소 권한 |
| SECURITY-09 | RDS 기본 자격 증명 변경, 디버그 모드 비활성화 |
| SECURITY-10 | Docker 이미지 pinned 버전, 취약점 스캔 |
