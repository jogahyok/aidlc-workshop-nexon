# Build Instructions — 테이블오더 서비스

## Prerequisites

| 도구 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 백엔드 서비스 |
| Node.js | 20+ | 프론트엔드 |
| pnpm | 8+ | 프론트엔드 패키지 관리 |
| Docker | 24+ | 컨테이너 빌드/실행 |
| Docker Compose | 2.20+ | 멀티 서비스 오케스트레이션 |
| dbmate | latest | DB 마이그레이션 |

## 환경 변수 설정

각 서비스의 `.env.example`을 `.env`로 복사하고 값을 설정:
```bash
cp services/auth-service/.env.example services/auth-service/.env
cp services/store-service/.env.example services/store-service/.env
# menu-service, order-service도 동일
```

---

## Build Steps

### 1. 백엔드 의존성 설치
```bash
# 각 서비스별 가상환경 생성 및 의존성 설치
cd services/auth-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../store-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../menu-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../order-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 프론트엔드 의존성 설치
```bash
cd frontend
pnpm install
```

### 3. Docker 이미지 빌드
```bash
# 프로젝트 루트에서
docker compose build
```

### 4. 데이터베이스 시작 및 마이그레이션
```bash
# MySQL 시작
docker compose up mysql -d

# 마이그레이션 실행 (dbmate)
dbmate -u "mysql://root:rootpassword@localhost:3306/auth_db" up --migrations-dir services/auth-service/migrations
dbmate -u "mysql://root:rootpassword@localhost:3306/store_db" up --migrations-dir services/store-service/migrations
dbmate -u "mysql://root:rootpassword@localhost:3306/menu_db" up --migrations-dir services/menu-service/migrations
dbmate -u "mysql://root:rootpassword@localhost:3306/order_db" up --migrations-dir services/order-service/migrations
```

### 5. 전체 서비스 시작
```bash
docker compose up -d
```

### 6. 프론트엔드 빌드
```bash
cd frontend
pnpm build
```

## 빌드 검증

| 확인 항목 | 명령어 | 기대 결과 |
|-----------|--------|-----------|
| Auth Service | `curl http://localhost:8001/health` | `{"status": "healthy"}` |
| Store Service | `curl http://localhost:8002/health` | `{"status": "healthy"}` |
| Menu Service | `curl http://localhost:8003/health` | `{"status": "healthy"}` |
| Order Service | `curl http://localhost:8004/health` | `{"status": "healthy"}` |
| Frontend build | `ls frontend/packages/customer-app/dist` | 빌드 파일 존재 |
