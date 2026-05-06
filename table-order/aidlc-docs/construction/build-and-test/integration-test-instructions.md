# Integration Test Instructions — Frontend (Unit 5)

## Purpose
프론트엔드와 백엔드 API 간 통합 테스트입니다.
백엔드 서비스(Auth, Store, Menu, Order)가 실행 중이어야 합니다.

## Prerequisites
- 백엔드 API 서버 실행 (개발자 A, B 유닛 완성 후)
- MySQL 데이터베이스 실행
- 테스트 데이터 시드

## Test Scenarios

### Scenario 1: Customer 주문 플로우
- **Description**: 메뉴 조회 → 옵션 선택 → 장바구니 → 주문 생성 → 주문 내역 확인
- **Setup**: 테스트 매장/테이블/메뉴 데이터 시드
- **Test Steps**:
  1. 테이블 자동 로그인 (GET /auth/me)
  2. 카테고리 조회 (GET /stores/{id}/categories)
  3. 메뉴 조회 (GET /stores/{id}/menus)
  4. 옵션 조회 (GET /menus/{id}/options)
  5. 주문 생성 (POST /stores/{id}/orders)
  6. 주문 내역 조회 (GET /stores/{id}/tables/{id}/orders)
- **Expected**: 주문 생성 성공, 주문 내역에 표시

### Scenario 2: Admin 로그인 + 주문 모니터링
- **Description**: 관리자 로그인 → 대시보드 → SSE 수신 → 상태 변경
- **Setup**: 관리자 계정 시드
- **Test Steps**:
  1. 관리자 로그인 (POST /auth/admin/login)
  2. 주문 목록 조회 (GET /stores/{id}/orders)
  3. SSE 연결 (GET /stores/{id}/orders/stream)
  4. 주문 상태 변경 (PATCH /orders/{id}/status)
- **Expected**: SSE로 실시간 주문 수신, 상태 변경 성공

### Scenario 3: Admin 테이블 이용 완료
- **Description**: 테이블 세션 종료 → 주문 이력 이동
- **Setup**: 활성 세션 + 주문 데이터
- **Test Steps**:
  1. 테이블 이용 완료 (POST /tables/{id}/complete)
  2. 과거 내역 조회 (GET /stores/{id}/tables/{id}/history)
- **Expected**: 현재 주문 사라짐, 과거 내역에 표시

## Run Integration Tests (MSW Mock 기반)

### 개발 단계 (백엔드 미완성 시)
```bash
# MSW로 API 모킹하여 통합 테스트
pnpm vitest --run --include '**/*.integration.test.ts'
```

### 실제 통합 테스트 (백엔드 완성 후)
```bash
# 백엔드 서버 실행 확인
curl http://localhost:8000/health

# 프론트엔드 통합 테스트 실행
VITE_API_URL=http://localhost:8000 pnpm test:integration
```

## Cleanup
- 테스트 데이터는 각 테스트 후 자동 정리 (트랜잭션 롤백)
- SSE 연결은 테스트 종료 시 자동 해제
