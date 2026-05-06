# Build Instructions — Frontend (Unit 5)

## Prerequisites
- **Node.js**: >= 20.0.0
- **pnpm**: >= 8.0.0 (`npm install -g pnpm`)
- **OS**: macOS / Linux / Windows

## Build Steps

### 1. Install Dependencies
```bash
cd table-order/frontend
pnpm install
```

### 2. Configure Environment
```bash
# Customer App (.env)
cp packages/customer-app/.env.example packages/customer-app/.env
# VITE_API_URL=http://localhost:8000/api
# VITE_APP_ENV=development

# Admin App (.env)
cp packages/admin-app/.env.example packages/admin-app/.env
# VITE_API_URL=http://localhost:8000/api
# VITE_APP_ENV=development
```

### 3. Build All Packages
```bash
# 전체 빌드
pnpm build

# 개별 빌드
pnpm build:customer
pnpm build:admin
```

### 4. Verify Build Success
- **Expected Output**: `✓ built in Xs` (각 앱별)
- **Build Artifacts**:
  - `packages/customer-app/dist/` — Customer App 정적 파일
  - `packages/admin-app/dist/` — Admin App 정적 파일
- **번들 크기 확인**: 각 앱 초기 로드 500KB 이하 (gzip)

### 5. Development Server
```bash
# Customer App (http://localhost:5173)
pnpm dev:customer

# Admin App (http://localhost:5174)
pnpm dev:admin
```

## Troubleshooting

### pnpm install 실패
- **원인**: Node.js 버전 불일치
- **해결**: `node --version` 확인 → 20+ 필요

### TypeScript 컴파일 에러
- **원인**: shared 패키지 참조 문제
- **해결**: `pnpm install` 재실행 → workspace 링크 확인

### Vite 프록시 연결 실패
- **원인**: 백엔드 서버 미실행
- **해결**: 백엔드 API 서버 실행 확인 (http://localhost:8000)
