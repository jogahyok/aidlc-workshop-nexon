# Deployment Architecture — Frontend (Unit 5)

## 배포 파이프라인

```
[git push] → [CodeBuild] → pnpm install → lint → test → build
  → [S3 Upload] → Customer/Admin 버킷
  → [CloudFront Invalidation] → 캐시 무효화
```

## 환경별 구성

| 환경 | Customer | Admin | API |
|------|----------|-------|-----|
| dev | customer-dev.tableorder.com | admin-dev.tableorder.com | api-dev.tableorder.com |
| prod | customer.tableorder.com | admin.tableorder.com | api.tableorder.com |

## 비용 추정: ~$7-12/월 (중규모)
