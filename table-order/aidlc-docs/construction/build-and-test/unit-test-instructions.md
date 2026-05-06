# Unit Test Execution — 테이블오더 서비스

## 백엔드 단위 테스트

### Auth Service
```bash
cd services/auth-service
source venv/bin/activate
pytest tests/ -v --hypothesis-seed=0
```

**테스트 항목:**
- `test_security.py` — JWT round-trip PBT, bcrypt 검증 PBT
- `test_auth_service.py` — 관리자/테이블 인증 로직
- `test_login_attempts.py` — 잠금 invariant PBT

**PBT 시드 로깅:** `--hypothesis-seed=0` (CI에서 고정 시드 사용)

### Store Service
```bash
cd services/store-service
source venv/bin/activate
pytest tests/ -v --hypothesis-seed=0
```

**테스트 항목:**
- `test_session_service.py` — 세션 상태 머신 PBT, 멱등성 PBT
- `test_table_service.py` — 테이블 관리 테스트
- `test_order_client.py` — 재시도 로직 테스트

### Menu Service
```bash
cd services/menu-service
source venv/bin/activate
pytest tests/ -v --hypothesis-seed=0
```

**테스트 항목:**
- `test_pbt_price.py` — 가격 계산 invariant PBT
- `test_option_rules.py` — 옵션 그룹 규칙 테스트

### Order Service
```bash
cd services/order-service
source venv/bin/activate
pytest tests/ -v --hypothesis-seed=0
```

**테스트 항목:**
- `test_pbt_order.py` — 주문 금액 계산 PBT
- `test_pbt_archive.py` — 아카이브 로직 PBT

---

## 프론트엔드 단위 테스트

```bash
cd frontend
pnpm test
```

**테스트 프레임워크:** Vitest + fast-check (PBT)

---

## 전체 테스트 한번에 실행

```bash
# 백엔드 전체
for svc in auth-service store-service menu-service order-service; do
  echo "=== Testing $svc ==="
  cd services/$svc
  source venv/bin/activate
  pytest tests/ -v --hypothesis-seed=0
  cd ../..
done

# 프론트엔드
cd frontend && pnpm test
```

## 기대 결과
- 모든 테스트 통과 (0 failures)
- PBT 시드 로깅 확인
- 커버리지: 핵심 비즈니스 로직 80% 이상
