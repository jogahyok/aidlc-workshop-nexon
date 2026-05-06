# Unit Test Execution — Frontend (Unit 5)

## Run Unit Tests

### 1. Execute All Unit Tests
```bash
cd table-order/frontend
pnpm test
```

### 2. Run Tests with Coverage
```bash
pnpm test:coverage
```

### 3. Run Specific Package Tests
```bash
# Shared 패키지만
pnpm --filter @table-order/shared test

# Customer App만
pnpm --filter @table-order/customer-app test

# Admin App만
pnpm --filter @table-order/admin-app test
```

### 4. Run PBT Tests Only
```bash
# PBT 파일만 실행
pnpm vitest --run --include '**/*.pbt.ts'
```

## Test Coverage Targets

| 패키지 | 목표 | 주요 테스트 대상 |
|--------|------|-----------------|
| shared | 80%+ | formatPrice, storageManager, 유틸리티 |
| customer-app | 60%+ | cartReducer, 비즈니스 로직 |
| admin-app | 60%+ | 인증 로직, API 호출 |

## Expected Results
- **Total Tests**: ~20+ (example-based + PBT)
- **PBT Tests**: 7 properties (formatPrice 4 + cartReducer 4)
- **Coverage**: 60% 이상 (비즈니스 로직 90%+)

## PBT Seed Logging
- fast-check 실패 시 seed 값이 출력됨
- 재현: `fc.assert(..., { seed: <failed-seed> })`

## Fix Failing Tests
1. 테스트 출력에서 실패 원인 확인
2. PBT 실패 시 shrunk minimal example 확인
3. 코드 수정 후 `pnpm test` 재실행
