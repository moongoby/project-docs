# WHY-DISPLAY 보고서 — 검증 페이지 매매 근거 표시

**작성일**: 2026-03-20
**태스크**: 검증 페이지에 "왜 이 종목? 왜 지금? 왜 매수/매도?" 근거 표시 추가

---

## 검증 체크리스트

- [x] **구현 목표**: 4개 검증 컴포넌트에 매매 근거(WHY) 필드 및 UI 표시 추가
- [x] **검증 방법**: `npm run build` 성공 + `curl http://localhost:3000/go100` → HTTP 307(정상 리다이렉트)
- [x] **완료 기준**: 빌드 성공(✓ Compiled successfully), 서비스 307 응답, 에러 로그 0건
- [x] **실패 기준**: TypeScript 컴파일 에러, 빌드 실패, 서비스 5xx 응답
- [x] **서비스 재시작 확인**: `systemctl restart go100-frontend` → 307 응답 확인
- [x] **에러 로그 0건**: `journalctl -u go100-frontend --since "1 min ago" | grep -i error` → 출력 없음

---

## 구현 내용

모든 4개 파일이 이미 구현 완료 상태였음. 빌드 및 서비스 재시작으로 검증.

### 수정 1: TradeHistory.tsx
- `SIGNAL_LABELS` 상수 (7종 매매 근거 한국어 라벨)
- `TradeItem` 인터페이스에 `signal_source`, `notes` 필드
- 테이블에 "근거" 컬럼 추가, 컬러 뱃지로 표시

### 수정 2: SignalTimeline.tsx
- `SignalItem` 인터페이스에 `signal_name`, `dip_pct`, `desk_id` 필드
- 시그널별 `signal_name`(보라), `dip_pct` 하락률(황색), `desk_id`(청록) 뱃지 표시

### 수정 3: TradeHistoryTable.tsx
- `Trade` 인터페이스에 `reason`, `regime_at_entry` 필드
- "진입근거" 컬럼 (cyan-300), "시장상태" 컬럼 (BULL=emerald, BEAR=red)

### 수정 4: TradeDetail.tsx
- `SIGNAL_LABELS` 상수 및 `signal_source` InfoRow 추가

---

## 빌드 결과

```
✓ Compiled successfully
✓ Generating static pages (51/51)
```

## 서비스 상태

```
curl http://localhost:3000/go100 → 307 (정상)
에러 로그 0건
```
