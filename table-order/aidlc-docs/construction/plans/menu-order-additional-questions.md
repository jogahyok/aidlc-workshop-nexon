# 추가 설계 질문 — Menu Service + Order Service (개발자 B)

## 개요
기존 7개 질문에서 다루지 못한 세부 설계 결정 사항입니다.
각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션의 알파벳을 입력해 주세요.

---

## Menu Service 추가 질문

### Question 8
카테고리 삭제 시 하위 메뉴가 존재하면 어떻게 처리하시겠습니까?

A) 하위 메뉴가 있으면 카테고리 삭제 불가 (에러 반환)
B) 하위 메뉴를 "미분류" 카테고리로 자동 이동 후 삭제
C) 하위 메뉴도 함께 소프트 삭제 (cascade)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 9
메뉴 목록 조회 시 정렬 및 필터링 옵션은 어떻게 하시겠습니까?

A) sort_order 기준 오름차순 고정 (클라이언트 정렬 불가)
B) sort_order 기본 + 가격순/이름순 정렬 파라미터 지원
C) sort_order 기본, 카테고리 필터만 지원 (정렬 변경 불가)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 10
메뉴 노출 순서(sort_order) 변경 방식은 어떻게 하시겠습니까?

A) 개별 메뉴의 sort_order 값을 직접 지정 (PUT /menus/{id})
B) 전체 순서를 배열로 한번에 전송 (PUT /stores/{store_id}/menus/reorder, body: [id1, id2, ...])
C) 위/아래 이동 API (POST /menus/{id}/move, body: {direction: "up"|"down"})
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 11
옵션 그룹이 없는 메뉴의 주문 처리는 어떻게 하시겠습니까?

A) 옵션 없이 바로 장바구니에 추가 가능 (옵션 선택 화면 스킵)
B) 항상 옵션 선택 화면을 거침 (옵션이 없으면 "옵션 없음" 표시 후 확인)
C) 옵션 유무에 따라 자동 분기 (있으면 모달, 없으면 바로 추가)
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 12
메뉴 이미지가 없는 경우 표시 방식은 어떻게 하시겠습니까?

A) 기본 플레이스홀더 이미지 표시 (서버에서 default_image_url 반환)
B) 이미지 영역 자체를 숨김 (텍스트만 표시)
C) 회색 플레이스홀더 + "이미지 없음" 텍스트 표시
X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 13
소프트 삭제된 메뉴를 복구할 수 있어야 합니까?

A) 복구 기능 필요 (관리자가 삭제된 메뉴 목록 조회 + 복구 가능)
B) 복구 불필요 (소프트 삭제는 기존 주문 참조용으로만 유지)
C) 일정 기간(예: 30일) 내에만 복구 가능, 이후 하드 삭제
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Order Service 추가 질문

### Question 14
주문 번호(order_number) 생성 규칙은 어떻게 하시겠습니까?

A) 매장 내 당일 일련번호 (001, 002, ... 매일 리셋)
B) 매장 내 전체 일련번호 (리셋 없이 계속 증가)
C) 타임스탬프 기반 (예: "20260506-001")
D) 세션별 일련번호 (테이블 세션 내에서 1, 2, 3...)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 15
주문 생성 시 세션(session_id) 검증은 어떻게 하시겠습니까?

A) Order Service가 Store Service에 세션 유효성 확인 HTTP 호출
B) JWT 토큰에 session_id가 포함되어 있으므로 토큰 검증만으로 충분
C) session_id는 클라이언트가 전송, 서버는 별도 검증 없이 저장만
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 16
동일 테이블에서 동시에 여러 주문이 생성될 때 처리는 어떻게 하시겠습니까?

A) 동시 주문 허용 (각각 독립 주문으로 생성)
B) 이전 주문이 "pending" 상태면 새 주문 생성 불가 (기존 주문에 추가 유도)
C) 동시 주문 허용하되, 같은 세션 내 주문은 시간순 정렬로 관리
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 17
SSE 연결 시 초기 데이터 전송은 어떻게 하시겠습니까?

A) 연결 즉시 현재 활성 주문(pending + preparing) 전체 목록 전송
B) 연결 후 이벤트만 수신 (초기 데이터는 별도 REST API로 조회)
C) 연결 시 최근 N분(예: 30분) 이내 주문만 전송
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 18
주문 조회 시 페이지네이션 방식은 어떻게 하시겠습니까?

A) 오프셋 기반 (page, size 파라미터)
B) 커서 기반 (last_id 파라미터, 무한 스크롤에 적합)
C) 고객 앱은 전체 조회 (세션 내 주문은 소량), 관리자 앱만 페이지네이션
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 19
주문 삭제 시 SSE 이벤트에 삭제된 주문의 상세 정보를 포함하시겠습니까?

A) order_id와 table_id만 전송 (최소 정보)
B) 삭제된 주문의 전체 정보 포함 (금액 재계산용)
C) order_id, table_id, total_amount 포함 (클라이언트 총액 재계산용)
X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 20
Menu Service 장애 시 주문 생성 fallback 전략은 어떻게 하시겠습니까?

A) Menu Service 불가 시 주문 완전 차단 (가격 검증 필수)
B) 캐시된 가격 정보로 검증 (최근 N분 이내 캐시 유효)
C) Menu Service 불가 시 가격 검증 스킵하고 주문 생성 (나중에 보정)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 21
과거 주문 이력(order_history) 조회 시 items_snapshot의 반환 형식은 어떻게 하시겠습니까?

A) JSON 그대로 반환 (클라이언트가 파싱)
B) 서버에서 파싱하여 구조화된 객체로 반환
C) 요약 정보만 반환 (총 항목 수, 총 금액), 상세는 별도 API
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 서비스 간 연동 추가 질문

### Question 22
내부 API(internal) 인증은 어떻게 하시겠습니까?

A) 별도 인증 없음 (내부 네트워크 신뢰, 외부 접근 차단으로 보안)
B) 서비스 간 공유 시크릿 키 (X-Internal-Key 헤더)
C) 서비스별 JWT 토큰 발급 (서비스 계정 인증)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 23
Order Service → Menu Service 가격 검증 시 여러 메뉴를 한번에 검증하시겠습니까?

A) 메뉴별 개별 호출 (GET /internal/menus/{id}/validate × N회)
B) 배치 검증 API (POST /internal/menus/validate-batch, body: [menu_id1, menu_id2, ...])
C) 주문 항목이 적으므로(보통 1~5개) 개별 호출로 충분
X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 24
아카이브 요청 시 해당 세션에 활성 주문(pending/preparing)이 남아있으면 어떻게 하시겠습니까?

A) 활성 주문 포함 모두 아카이브 (상태 무관하게 전부 이동)
B) 활성 주문이 있으면 아카이브 거부 (모든 주문이 completed여야 함)
C) 활성 주문은 강제로 completed 처리 후 아카이브
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 답변 완료 후
이 파일에 답변을 기입하신 후 커밋해 주세요.
답변을 기반으로 비즈니스 로직 설계 문서를 보완하겠습니다.
