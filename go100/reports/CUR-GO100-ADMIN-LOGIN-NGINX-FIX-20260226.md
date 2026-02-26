# CUR-GO100-ADMIN-LOGIN-NGINX-FIX + DATA-ACCURACY-001

**날짜**: 2026-02-26
**코드 레포**: kis-autotrade-v4 (branch: `phase-2c-command-center`)
**커밋**: `87eca856` (Context Continuity + Login Fix), `db005081` (Data Accuracy)

---

## 1. trading41.newtalk.kr /admin/login.html 접속 불가 수정

### 문제
- `https://trading41.newtalk.kr/admin/login.html` 접속 시 로그인 폼 대신 랜딩 페이지 표시
- 원인: `/admin/login.html` 파일 미존재 → nginx `try_files` → `index.html` 폴백

### 조치
- nginx (`/etc/nginx/sites-enabled/kis-autotrade`) HTTP(80) + HTTPS(443) 양쪽에 리다이렉트 추가:
```nginx
location ~ ^/admin/login(\.html)?$ {
    return 302 /login.html;
}
```

### 확인
| URL | 결과 |
|-----|------|
| `/admin/login.html` | 302 → `/login.html` |
| `/admin/login` | 302 → `/login.html` |
| `/login.html` | 200 (로그인 폼 정상 표시) |

---

## 2. CUR-GO100-DATA-ACCURACY-001 — 데이터 정확도 개선

### 2-1. 응답 포맷 개선
- stock_info, market_briefing 리스트 항목 들여쓰기 통일 (`  1.`, `  2.`)
- 시장 브리핑 5일 추이: 한 줄 → 줄바꿈 리스트로 변경 (가독성 향상)

### 2-2. 스크리닝 요청 vs 실행 조건 불일치 안내
- 사용자가 "이평선 정배열" 같은 미지원 조건 요청 시 → 실행된 조건 안내 메시지 추가
- `get_requested_screening_label()`: 메시지에서 요청 조건 라벨 추출
- 요청 라벨 ≠ 실행 라벨이면: "⚠️ 요청 조건은 준비 중, 대신 [OO]으로 검색" 표시

### 2-3. 할루시네이션 필터 강화
- 거래량 500배 초과 수치 감지 추가 (`_find_volume_ratios`)
- `HallucinationReport.high_volume_ratios` 필드
- sanitize_reply에 경고 문구: "거래량 500배 초과 수치는 데이터 오류일 수 있어 확인 필요"

### 수정 파일
| 파일 | 변경 |
|------|------|
| `backend/app/routers/go100/ai_router.py` | 포맷 개선 + 스크리닝 불일치 안내 |
| `backend/app/services/go100/ai/response_filter.py` | 거래량 배수 할루시네이션 필터 |
| `backend/app/services/go100/screening_engine.py` | 요청 라벨 추출 + 포맷 들여쓰기 |
