# Tech Stack Decisions — Frontend (Unit 5)

## 개요
프론트엔드 유닛의 기술 스택 세부 결정 사항입니다.

---

## 1. 핵심 기술 스택

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| 프레임워크 | React | ^18.3 | 생태계 성숙도, 커뮤니티 지원 |
| 언어 | TypeScript | ^5.4 | 타입 안전성, 개발 생산성 |
| 빌드 도구 | Vite | ^5.4 | 빠른 HMR, ESM 기반, 설정 간단 |
| 패키지 관리 | pnpm | ^8.15 | 디스크 효율, 엄격한 의존성 관리 |
| 모노레포 | pnpm workspaces | - | 추가 도구 불필요, pnpm 내장 |

## 2. UI 레이어

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| UI 라이브러리 | MUI (Material UI) | ^5.15 | 풍부한 컴포넌트, 접근성 내장, 테마 시스템 |
| 아이콘 | @mui/icons-material | ^5.15 | MUI 통합 |
| 라우팅 | React Router | ^6.22 | SPA 표준, 코드 스플리팅 지원 |

## 3. 상태 관리 및 데이터

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| 서버 상태 | TanStack Query | ^5.28 | 캐싱, 자동 재시도, 폴링, 낙관적 업데이트 |
| HTTP 클라이언트 | Axios | ^1.6 | 인터셉터, 요청 취소, 타입 지원 |
| 전역 상태 | React Context + useReducer | - | 가벼움, 추가 의존성 없음 |
| 로컬 저장 | localStorage | - | 브라우저 내장, 장바구니/토큰 저장 |

## 4. 폼 및 검증

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| 폼 관리 | React Hook Form | ^7.51 | 비제어 컴포넌트 기반, 높은 성능 |
| 스키마 검증 | Zod | ^3.22 | TypeScript 네이티브, 런타임 검증 |
| 폼-스키마 연동 | @hookform/resolvers | ^3.3 | RHF + Zod 통합 |

## 5. 테스트

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| 테스트 러너 | Vitest | ^1.4 | Vite 네이티브, Jest 호환 API |
| 컴포넌트 테스트 | React Testing Library | ^14.2 | 사용자 관점 테스트, 접근성 쿼리 |
| PBT 프레임워크 | fast-check | ^3.17 | TypeScript 지원, shrinking, seed 재현 |
| 모킹 | MSW (Mock Service Worker) | ^2.2 | 네트워크 레벨 모킹, 테스트/개발 공용 |

## 6. 개발 도구

| 영역 | 기술 | 버전 | 선택 근거 |
|------|------|------|-----------|
| 린터 | ESLint | ^8.57 | 코드 품질, TypeScript 규칙 |
| ESLint 플러그인 | @typescript-eslint | ^7.3 | TS 전용 규칙 |
| ESLint 플러그인 | eslint-plugin-react-hooks | ^4.6 | 훅 규칙 검사 |
| 포매터 | Prettier | ^3.2 | 코드 스타일 통일 |
| Git 훅 | Husky | ^9.0 | 커밋 전 자동 검사 |
| 스테이징 린트 | lint-staged | ^15.2 | 변경 파일만 린트 |

## 7. 브라우저 지원

| 브라우저 | 최소 버전 | 비고 |
|----------|-----------|------|
| Chrome | 최신 2버전 | 태블릿 기본 브라우저 |
| Edge | 최신 2버전 | Chromium 기반 |
| Firefox | 최신 2버전 | 모바일 QR 접속 대응 |
| Safari | 최신 2버전 | iOS QR 접속 대응 |

### Vite browserslist 설정
```
last 2 Chrome versions
last 2 Edge versions
last 2 Firefox versions
last 2 Safari versions
```

---

## 8. 프로젝트 구조 (최종)

```
frontend/
├── packages/
│   ├── shared/                    # 공통 라이브러리
│   │   ├── src/
│   │   │   ├── components/        # Button, Card, Modal, Toast 등
│   │   │   ├── hooks/             # useAuth, useApi, useLocalStorage
│   │   │   ├── types/             # 공통 타입 정의
│   │   │   ├── utils/             # formatPrice, formatDate, apiClient
│   │   │   └── index.ts           # 배럴 export
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── customer-app/              # 고객용 앱
│   │   ├── src/
│   │   │   ├── pages/             # MenuPage, CartPage, OrderHistoryPage
│   │   │   ├── components/        # MenuCard, CartItem, OptionGroup
│   │   │   ├── contexts/          # AuthContext, CartContext
│   │   │   ├── hooks/             # useCart, useOrders
│   │   │   ├── api/               # API 호출 함수
│   │   │   ├── schemas/           # Zod 스키마
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── admin-app/                 # 관리자용 앱
│       ├── src/
│       │   ├── pages/             # LoginPage, Dashboard, TableMgmt, MenuMgmt
│       │   ├── components/        # TableCard, OrderDetail, MenuForm
│       │   ├── contexts/          # AuthContext
│       │   ├── hooks/             # useSSE, useOrders, useTables
│       │   ├── api/               # API 호출 함수
│       │   ├── schemas/           # Zod 스키마
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── index.html
│       ├── vite.config.ts
│       ├── package.json
│       └── tsconfig.json
├── package.json                   # 모노레포 루트 (scripts, devDependencies)
├── pnpm-workspace.yaml            # 워크스페이스 정의
├── tsconfig.base.json             # 공통 TS 설정
├── .eslintrc.cjs                  # 공통 ESLint 설정
├── .prettierrc                    # Prettier 설정
└── vitest.workspace.ts            # Vitest 워크스페이스 설정
```

---

## 9. 의존성 요약

### 프로덕션 의존성
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.22.3",
  "@mui/material": "^5.15.14",
  "@mui/icons-material": "^5.15.14",
  "@emotion/react": "^11.11.4",
  "@emotion/styled": "^11.11.5",
  "@tanstack/react-query": "^5.28.9",
  "axios": "^1.6.8",
  "react-hook-form": "^7.51.2",
  "@hookform/resolvers": "^3.3.4",
  "zod": "^3.22.4"
}
```

### 개발 의존성
```json
{
  "typescript": "^5.4.3",
  "vite": "^5.4.2",
  "@vitejs/plugin-react": "^4.2.1",
  "vitest": "^1.4.0",
  "@testing-library/react": "^14.2.2",
  "@testing-library/jest-dom": "^6.4.2",
  "fast-check": "^3.17.1",
  "msw": "^2.2.3",
  "eslint": "^8.57.0",
  "@typescript-eslint/eslint-plugin": "^7.3.1",
  "@typescript-eslint/parser": "^7.3.1",
  "eslint-plugin-react-hooks": "^4.6.0",
  "prettier": "^3.2.5",
  "husky": "^9.0.11",
  "lint-staged": "^15.2.2"
}
```

---

## 10. 빌드 및 배포 고려사항

### 빌드 최적화
- Vite 프로덕션 빌드: minification + tree-shaking
- 코드 스플리팅: React.lazy + Suspense (페이지 단위)
- 소스맵: 프로덕션에서 hidden-source-map (에러 리포팅용, 공개 안 함)

### CI/CD 파이프라인 (향후)
- `pnpm install --frozen-lockfile`
- `pnpm lint` (ESLint)
- `pnpm test` (Vitest + fast-check)
- `pnpm audit` (의존성 보안 검사)
- `pnpm build` (프로덕션 빌드)
- 번들 크기 체크 (500KB 초과 시 경고)
