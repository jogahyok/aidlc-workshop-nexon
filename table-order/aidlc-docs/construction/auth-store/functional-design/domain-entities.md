# 도메인 엔티티 — Auth Service + Store Service

## Auth Service 엔티티

### Admin (관리자)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 관리자 고유 ID |
| store_id | INT | FK(stores.id), NOT NULL | 소속 매장 |
| username | VARCHAR(50) | NOT NULL, UNIQUE per store | 사용자명 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 해시 비밀번호 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | 생성 시각 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | 수정 시각 |

**제약사항:**
- 매장당 1개 관리자 계정 (store_id UNIQUE)
- username은 매장 내 고유

---

### TableCredential (테이블 인증 정보)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 고유 ID |
| store_id | INT | FK(stores.id), NOT NULL | 소속 매장 |
| table_id | INT | FK(tables.id), NOT NULL, UNIQUE | 연결된 테이블 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 해시 비밀번호 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | 생성 시각 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | 수정 시각 |

**제약사항:**
- 테이블당 1개 인증 정보 (table_id UNIQUE)

---

### LoginAttempt (로그인 시도 기록)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 고유 ID |
| store_id | INT | NOT NULL | 대상 매장 |
| identifier | VARCHAR(100) | NOT NULL | 로그인 식별자 (username 또는 table_number) |
| attempt_type | ENUM('admin', 'table') | NOT NULL | 시도 유형 |
| success | BOOLEAN | NOT NULL | 성공 여부 |
| ip_address | VARCHAR(45) | NULL | 요청 IP |
| attempted_at | DATETIME | NOT NULL, DEFAULT NOW | 시도 시각 |

**인덱스:**
- (store_id, identifier, attempt_type, attempted_at) — 잠금 판단용 조회

---

### JWT Token Payload
```json
{
  "sub": "<admin_id 또는 table_id>",
  "store_id": "<매장 ID>",
  "type": "admin | table",
  "table_number": "<테이블 번호 (table 타입만)>",
  "iat": "<발급 시각>",
  "exp": "<만료 시각 (발급 + 16시간)>"
}
```

---

## Store Service 엔티티

### Store (매장)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 매장 고유 ID |
| name | VARCHAR(100) | NOT NULL | 매장명 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | 매장 식별 코드 (로그인 시 사용) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | 생성 시각 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | 수정 시각 |

**제약사항:**
- code는 시스템 전체에서 고유 (매장 식별자로 사용)

---

### Table (테이블)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 테이블 고유 ID |
| store_id | INT | FK(stores.id), NOT NULL | 소속 매장 |
| table_number | INT | NOT NULL | 테이블 번호 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | 생성 시각 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | 수정 시각 |

**제약사항:**
- (store_id, table_number) UNIQUE — 매장 내 테이블 번호 고유

---

### TableSession (테이블 세션)
| 필드 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INT | PK, AUTO_INCREMENT | 세션 고유 ID |
| table_id | INT | FK(tables.id), NOT NULL | 대상 테이블 |
| store_id | INT | FK(stores.id), NOT NULL | 소속 매장 |
| status | ENUM('active', 'completed') | NOT NULL, DEFAULT 'active' | 세션 상태 |
| started_at | DATETIME | NOT NULL, DEFAULT NOW | 세션 시작 시각 |
| completed_at | DATETIME | NULL | 세션 종료 시각 |

**제약사항:**
- 테이블당 active 세션은 최대 1개 (table_id + status='active' UNIQUE)

**인덱스:**
- (table_id, status) — 현재 활성 세션 조회
- (store_id, status) — 매장별 활성 세션 목록
