# Deployment Architecture — Auth Service + Store Service

## 배포 아키텍처 다이어그램

```
                    Internet
                       |
                       v
              +--------+--------+
              |      ALB        |
              | (HTTPS:443)     |
              | Public Subnet   |
              +--------+--------+
                       |
            Path-based routing
                       |
         +------+------+------+------+
         |      |      |      |      |
         v      v      v      v      v
    +----+--+ +-+---+ +-+---+ +-+---+
    | Auth  | |Store| |Menu | |Order|
    | :8001 | |:8002| |:8003| |:8004|
    +-------+ +-----+ +-----+ +-----+
         |      |      |      |
         +------+------+------+
                |
         EC2 Instance (Docker Compose)
         Private Subnet A
                |
                v
         +------+------+
         |   RDS MySQL |
         | db.t3.micro |
         | Private Sub |
         +-------------+
```

---

## 배포 프로세스

### 1. 이미지 빌드
```bash
# 각 서비스 디렉토리에서
docker build -t auth-service:v1.0.0 ./services/auth-service/
docker build -t store-service:v1.0.0 ./services/store-service/
```

### 2. 이미지 푸시 (ECR)
```bash
# ECR 리포지토리에 푸시
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag auth-service:v1.0.0 <account>.dkr.ecr.<region>.amazonaws.com/auth-service:v1.0.0
docker push <account>.dkr.ecr.<region>.amazonaws.com/auth-service:v1.0.0
```

### 3. EC2 배포
```bash
# EC2에서 최신 이미지 pull 및 재시작
ssh ec2-user@<instance>
docker compose pull
docker compose up -d
```

---

## 환경 구성

### 환경변수 관리
| 환경 | 방식 | 비고 |
|------|------|------|
| 로컬 개발 | .env 파일 | Git 제외 (.gitignore) |
| EC2 배포 | docker-compose.yml + .env | EC2 인스턴스 내 |
| 시크릿 | AWS Secrets Manager | JWT_SECRET_KEY, DB_PASSWORD |

### docker-compose.yml (프로덕션)
```yaml
version: "3.8"

services:
  auth-service:
    image: ${ECR_REGISTRY}/auth-service:${VERSION}
    ports:
      - "8001:8000"
    env_file:
      - ./auth-service.env
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  store-service:
    image: ${ECR_REGISTRY}/store-service:${VERSION}
    ports:
      - "8002:8000"
    env_file:
      - ./store-service.env
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## DB 마이그레이션 배포

```bash
# dbmate를 사용한 마이그레이션 실행
# Auth Service
dbmate -u "mysql://user:pass@rds-endpoint:3306/auth_db" up

# Store Service
dbmate -u "mysql://user:pass@rds-endpoint:3306/store_db" up
```

---

## 모니터링 및 로깅

| 항목 | 서비스 | 비고 |
|------|--------|------|
| 컨테이너 로그 | CloudWatch Logs (Docker log driver) | JSON 포맷 |
| ALB 로그 | S3 버킷 | SECURITY-02 |
| RDS 모니터링 | CloudWatch (기본 메트릭) | CPU, 연결 수, 스토리지 |
| 헬스체크 | ALB Target Group | /health 엔드포인트 |
| 알림 | CloudWatch Alarms | CPU > 80%, 5xx 에러 증가 |

---

## 비용 추정 (월간, ap-northeast-2 기준)

| 리소스 | 예상 비용 |
|--------|-----------|
| EC2 t3.small (24/7) | ~$15 |
| RDS db.t3.micro (24/7) | ~$12 |
| ALB | ~$16 + 트래픽 |
| NAT Gateway | ~$32 + 트래픽 |
| S3 (이미지 + 로그) | ~$1 |
| ECR | ~$1 |
| **합계** | **~$77/월** |
