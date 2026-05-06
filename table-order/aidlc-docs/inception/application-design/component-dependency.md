# 컴포넌트 의존성

## 의존성 매트릭스

| 컴포넌트 (행 → 열에 의존) | Auth | Store | Menu | Order | MySQL | S3 | Gateway |
|---------------------------|------|-------|------|-------|-------|-----|---------|
| **Auth Service** | - | - | - | - | ✅ | - | - |
| **Store Service** | - | - | - | ✅ | ✅ | - | - |
| **Menu Service** | - | - | - | - | ✅ | ✅ | - |
| **Order Service** | - | - | ✅ | - | ✅ | - | - |
| **API Gateway** | ✅ | - | - | - | - | - | - |
| **Customer App** | - | - | - | - | - | - | ✅ |
| **Admin App** | - | - | - | - | - | - | ✅ |

---

## 통신 패턴 상세

### API Gateway → 백엔드 서비스
```
Customer App / Admin App
        |
        v
+------------------+
|   API Gateway    |
|  (ALB + Nginx)   |
+------------------+
        |
   Path-based routing:
   /api/auth/*   → Auth Service
   /api/stores/* → Store Service
   /api/menus/*  → Menu Service
   /api/orders/* → Order Service
```

### 서비스 간 직접 통신
```
Store Service --[HTTP]--> Order Service
  (세션 종료 시 주문 아카이브 요청)

Order Service --[HTTP]--> Menu Service
  (주문 생성 시 가격 검증)
```

### SSE 실시간 스트림
```
Order Service --[SSE]--> Admin App
  (새 주문, 상태 변경, 주문 삭제 이벤트)

Order Service --[SSE]--> Customer App (선택)
  (주문 상태 변경 이벤트)
```

---

## 데이터 흐름

### 고객 주문 플로우
```
1. Customer App → Gateway → Menu Service: 메뉴/옵션 조회
2. Customer App: 장바구니 관리 (로컬)
3. Customer App → Gateway → Order Service: 주문 생성
4. Order Service → Menu Service: 가격 검증 (HTTP)
5. Order Service: 주문 저장 (MySQL)
6. Order Service → Admin App: SSE 이벤트 (새 주문)
```

### 관리자 테이블 이용 완료 플로우
```
1. Admin App → Gateway → Store Service: 테이블 이용 완료 요청
2. Store Service → Order Service: 세션 주문 아카이브 요청 (HTTP)
3. Order Service: 주문 → 주문 이력 이동 (MySQL)
4. Store Service: 세션 종료 처리 (MySQL)
5. Store Service → Admin App: 응답 (성공/실패)
```

### 관리자 주문 상태 변경 플로우
```
1. Admin App → Gateway → Order Service: 상태 변경 요청
2. Order Service: 상태 업데이트 (MySQL)
3. Order Service → Admin App: SSE 이벤트 (상태 변경)
4. Order Service → Customer App: SSE 이벤트 (상태 변경, 선택)
```

---

## 배포 단위

| 배포 단위 | 포함 서비스 | 스케일링 |
|-----------|-------------|----------|
| auth-service | Auth Service | 독립 스케일링 |
| store-service | Store Service | 독립 스케일링 |
| menu-service | Menu Service | 독립 스케일링 |
| order-service | Order Service | 독립 스케일링 (SSE 연결 고려) |
| customer-app | Customer App (정적 파일) | CDN/S3 |
| admin-app | Admin App (정적 파일) | CDN/S3 |
