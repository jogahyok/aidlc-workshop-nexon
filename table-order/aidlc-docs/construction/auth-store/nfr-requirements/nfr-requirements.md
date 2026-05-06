# NFR Requirements — Auth Service + Store Service

## 1. 성능 요구사항

### 응답 시간
| API | 목표 | 비고 |
|-----|------|------|
| POST /auth/admin/login | 1초 이내 | bcrypt 해싱 포함 |
| POST /auth/table/login | 1초 이내 | bcrypt 해싱 포함 |
| GET /auth/me (토큰 검증) | 100ms 이내 | JWT 디코딩만 |
| GET /stores/{id}/tables | 500ms 이내 | DB 조회 |
| POST /stores/{id}/tables/{id}/complete | 2초 이내 | Order Service 연동 포함 |

### 동시 접속
- 매장당 10~50 테이블 동시 접속
- 관리자 동시 접속: 매장당 1명
- 다중 매장 지원: 수십 개 매장 동시 운영

### 처리량
- 로그인 요청: 초당 10건 이상 처리 가능
- 토큰 검증: 초당 100건 이상 처리 가능 (모든 API 요청마다 수행)

---

## 2. 보안 요구사항

### SECURITY-01: 암호화
- DB 연결: TLS 1.2+ 강제 (MySQL SSL 모드)
- 비밀번호: bcrypt 해싱 (cost factor 12)
- JWT Secret: 환경변수, 최소 32자

### SECURITY-03: 애플리케이션 로깅
- Python 표준 logging 사용
- JSON 형식 출력 (production)
- 필수 필드: timestamp, request_id, level, message
- 민감 정보 로깅 금지 (password, token 값)

### SECURITY-05: 입력 검증
- Pydantic 스키마로 모든 API 입력 검증
- 문자열 최대 길이 제한 (username: 50자, password: 128자)
- 요청 본문 크기 제한 (1MB)

### SECURITY-08: 접근 제어
- 모든 엔드포인트 인증 필수 (로그인 제외)
- 관리자 전용 엔드포인트: type='admin' 검증
- 매장 격리: store_id 기반 데이터 접근 제한 (IDOR 방지)
- CORS: 허용된 오리진만 설정

### SECURITY-09: 보안 강화
- 에러 응답에 내부 정보 노출 금지
- 기본 자격 증명 없음
- 프로덕션 디버그 모드 비활성화

### SECURITY-11: 보안 설계
- 인증 로직 전용 모듈 분리 (core/security.py)
- Rate Limiting: 로그인 엔드포인트 (5회/15분 잠금)
- 방어 계층: 입력 검증 → 잠금 확인 → 인증 → 토큰 발급

### SECURITY-12: 인증 및 자격 증명 관리
- bcrypt 적응형 해싱 (cost factor 12)
- 세션 만료: 16시간
- Brute-force 방지: 5회 실패 시 15분 잠금
- 하드코딩된 자격 증명 없음 (환경변수 사용)

### SECURITY-15: 예외 처리
- 글로벌 예외 핸들러 (FastAPI exception_handler)
- 외부 호출(DB, HTTP) 명시적 에러 처리
- 실패 시 접근 거부 (fail closed)
- 리소스 정리 (DB 커넥션 반환)

---

## 3. 가용성 요구사항

- 서비스 가동률 목표: 99.5%
- 헬스체크 엔드포인트: GET /health (DB 연결 확인 포함)
- 그레이스풀 셧다운 지원
- DB 커넥션 풀 관리 (연결 끊김 자동 재연결)

---

## 4. 유지보수성 요구사항

- FastAPI 내장 Swagger 자동 문서화
- Pydantic 스키마로 API 계약 명확화
- dbmate로 DB 마이그레이션 버전 관리
- 테스트 커버리지: 핵심 비즈니스 로직 80% 이상
