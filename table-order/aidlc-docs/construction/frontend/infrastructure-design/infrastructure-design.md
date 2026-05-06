# Infrastructure Design — Frontend (Unit 5)

## 개요
프론트엔드 유닛의 AWS 인프라 설계입니다.
정적 파일 호스팅 (S3 + CloudFront) 기반으로 구성합니다.

---

## 1. 인프라 구성 요약

| 컴포넌트 | AWS 서비스 | 용도 |
|----------|-----------|------|
| 정적 파일 저장 | S3 | 빌드된 HTML/JS/CSS 호스팅 |
| CDN | CloudFront | 글로벌 캐싱, HTTPS 종료, 보안 헤더 |
| SSL 인증서 | ACM (Certificate Manager) | HTTPS 인증서 관리 |
| DNS | Route 53 | 도메인 라우팅 |

---

## 2. S3 버킷 구성

### Customer App 버킷
- **버킷명**: `tableorder-customer-{env}`
- **접근**: CloudFront OAI를 통해서만 접근
- **퍼블릭 접근**: 차단 (Block all public access)
- **암호화**: SSE-S3
- **버전 관리**: 활성화

### Admin App 버킷
- **버킷명**: `tableorder-admin-{env}`
- **설정**: Customer App과 동일

---

## 3. CloudFront 배포

- **Customer App 도메인**: customer.tableorder.com
- **Admin App 도메인**: admin.tableorder.com
- **캐시**: HTML no-cache, JS/CSS 1년 (해시 파일명)
- **SPA 라우팅**: 404 → /index.html (200)
- **압축**: Gzip + Brotli
- **보안 헤더**: CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy

---

## 4. 로컬 개발 환경

```bash
# Customer App: http://localhost:5173
pnpm --filter customer-app dev

# Admin App: http://localhost:5174
pnpm --filter admin-app dev
```

Vite 프록시로 백엔드 API 연결 (`/api` → `http://localhost:8000`)
