# 서비스 레이어 설계

## 서비스 아키텍처 개요

```
+------------------+
|   API Gateway    |  (라우팅, 인증 검증, CORS, Rate Limit)
+------------------+
        |
   +----+----+----+----+
   |    |    |    |    |
   v    v    v    v    v
+------+ +------+ +------+ +------+
| Auth | | Store| | Menu | | Order|
| Svc  | | Svc  | | Svc  | | Svc  |
+------+ +------+ +------+ +------+
   |         |        |        |
   +----+----+----+----+----+--+
        |              |
   +----v----+    +----v----+
   |  MySQL  |    |   S3    |
   |  (RDS)  |    | (Image) |
   +---------+    +---------+
```

---

## 서비스 정의

### Auth Service
- **책임 범위**: 인증/인가 전담
- **오케스트레이션**: 독립적 (다른 서비스에 의존하지 않음)
- **트랜잭션 경계**: 로그인 시도 기록, 토큰 발급은 단일 트랜잭션
- **외부 의존**: MySQL (admins, table_credentials 테이블), Raw SQL 쿼리 + 데이터 매퍼

### Store Service
- **책임 범위**: 매장/테이블/세션 관리
- **오케스트레이션**: 
  - 테이블 이용 완료 시 → Order Service에 세션 주문 아카이브 요청 (HTTP 호출)
- **트랜잭션 경계**: 세션 종료는 Store Service 내 트랜잭션, 주문 아카이브는 Order Service 트랜잭션
- **외부 의존**: MySQL, Order Service (HTTP)

### Menu Service
- **책임 범위**: 메뉴/카테고리/옵션 CRUD, 이미지 관리
- **오케스트레이션**: 독립적 (다른 서비스에 의존하지 않음)
- **트랜잭션 경계**: 메뉴 삭제 시 관련 옵션 그룹도 함께 삭제 (cascade)
- **외부 의존**: MySQL, S3 (이미지 업로드 URL 생성)

### Order Service
- **책임 범위**: 주문 생성/조회/상태 관리/삭제/이력/실시간 스트림
- **오케스트레이션**:
  - 주문 생성 시 → Menu Service에서 메뉴/옵션 가격 검증 (HTTP 호출)
  - 주문 상태 변경/생성 시 → SSE 연결된 클라이언트에 이벤트 푸시
- **트랜잭션 경계**: 주문 생성(order + order_items + order_item_options)은 단일 트랜잭션
- **외부 의존**: MySQL, Menu Service (HTTP, 가격 검증)

---

## 서비스 간 통신 패턴

### 동기 통신 (HTTP/REST)
| 호출자 | 대상 | 목적 | 실패 처리 |
|--------|------|------|-----------|
| Order Service | Menu Service | 주문 시 메뉴/옵션 가격 검증 | 주문 거부, 에러 반환 |
| Store Service | Order Service | 세션 종료 시 주문 아카이브 | 재시도 후 실패 시 에러 반환 |
| API Gateway | Auth Service | 토큰 검증 | 401 Unauthorized 반환 |

### 비동기 통신 (SSE)
| 발행자 | 구독자 | 이벤트 |
|--------|--------|--------|
| Order Service | Admin App | 새 주문 생성, 주문 상태 변경, 주문 삭제 |
| Order Service | Customer App (선택) | 주문 상태 변경 |

---

## 데이터 소유권

| 서비스 | 소유 데이터 | 읽기 전용 접근 |
|--------|-------------|----------------|
| Auth Service | admins, table_credentials, login_attempts | - |
| Store Service | stores, tables, table_sessions | - |
| Menu Service | categories, menu_items, option_groups, option_items | - |
| Order Service | orders, order_items, order_item_options, order_history | - |

각 서비스는 자신의 데이터만 직접 접근하며, 다른 서비스의 데이터는 HTTP API를 통해 조회합니다.

---

## 공통 패턴

### 에러 처리
- 각 서비스는 표준화된 에러 응답 형식 사용
- HTTP 상태 코드 + 에러 코드 + 메시지 구조
- 글로벌 예외 핸들러로 미처리 예외 포착

### 데이터 접근
- Raw SQL 쿼리 (파라미터화된 쿼리로 SQL Injection 방지)
- 데이터 매퍼 패턴으로 쿼리 결과를 도메인 객체로 변환
- 커넥션 풀 관리 (aiomysql 또는 databases 라이브러리)
- 트랜잭션 관리를 위한 컨텍스트 매니저 패턴

### 로깅
- 구조화된 JSON 로깅
- 요청 ID (correlation ID) 전파
- 민감 정보 마스킹

### 헬스체크
- 각 서비스 `/health` 엔드포인트 제공
- DB 연결 상태 확인 포함
