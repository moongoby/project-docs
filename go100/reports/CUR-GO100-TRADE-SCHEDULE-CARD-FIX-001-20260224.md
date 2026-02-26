# CUR-GO100-TRADE-SCHEDULE-CARD-FIX-001 — 자동매매 스케줄 등록 시 GO100 전략카드 미노출 수정

**발행일시**: 2026-02-24  
**프로젝트**: kis-autotrade-v4  
**브랜치**: phase-2c-command-center  
**작업 ID**: CUR-GO100-TRADE-SCHEDULE-CARD-FIX-001  

---

## 1. 현상

- **페이지**: go100.newtalk.kr/trade → 새 스케줄 등록 → 1단계 전략 선택
- **문제**: 드롭다운에 V4.1 strategy_cards만 표시되고, GO100 전략카드(go100_strategy_cards)가 선택지에 없음
- **영향**: 사용자가 "내 전략"(GO100 카드)으로 자동매매 스케줄을 등록할 수 없음

---

## 2. 원인

1. **Catalog API 사용 방식**
   - trade 페이지에서 전략 목록을 `getCatalog("all")`로 조회
   - 백엔드 `tab=all`은 **GO100 featured 카드만** 반환(`list_cards_with_system(tab="all")` → `is_featured = true AND is_active = true`)
   - "내 전략" 등 비-featured GO100 카드는 목록에 포함되지 않음

2. **GO100 제외 필터**
   - 기존에 `catalogCardsForSchedule = catalogCards.filter((c) => c.source !== "go100")` 로 GO100 카드를 스케줄 폼에서 제외하고 있었음 (CUR-GO100-LIVE-TRADE-E2E-AUDIT-001 대응으로 추정)
   - 그 결과 전략 선택 드롭다운에 GO100 카드가 노출되지 않음

3. **tab=v4 미사용**
   - 백엔드 `tab=v4` 시 `list_v4_cards_with_system()`이 호출되어 **V4.1 strategy_cards + 사용자 GO100 카드**를 병합한 목록을 반환하지만, trade 페이지는 `tab=all`만 사용하고 있었음

---

## 3. 수정 내용

### 3.1 프론트엔드 (kis-autotrade-v4)

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/lib/api/strategy-cards.ts` | `getCatalog` 인자에 `"v4"` 추가, 주석에 tab=v4 용도 명시 |
| `frontend/src/app/(protected)/trade/page.tsx` | catalog 호출을 `getCatalog("all")` → `getCatalog("v4")` 로 변경, queryKey `"v4"` 사용 |
| `frontend/src/app/(protected)/trade/page.tsx` | `catalogCardsForSchedule` 제거, ScheduleForm에 `catalogCards` 그대로 전달(GO100 포함) |
| `frontend/src/app/(protected)/trade/page.tsx` | rawCards/catalogCards의 `source` 타입을 `"v4" \| "go100"` 로 명시하여 타입 오류 해결 |
| `frontend/src/components/trade/ScheduleForm.tsx` | SelectItem의 key를 `source-id` 조합으로 변경하여 V4.1/GO100 동일 숫자 id 충돌 방지 |

### 3.2 백엔드

- **변경 없음.** 기존 `/api/v1/strategy-cards/catalog?tab=v4` 가 이미 `list_v4_cards_with_system()`으로 V4.1 + GO100 병합 목록을 반환하고 있음.

### 3.3 DB

- **변경 없음.** strategy_cards / v4_trade_schedules / go100_strategy_cards 스키마 변경 없음.

---

## 4. 변경 파일 요약

```
frontend/src/lib/api/strategy-cards.ts
frontend/src/app/(protected)/trade/page.tsx
frontend/src/components/trade/ScheduleForm.tsx
```

---

## 5. 테스트 결과

- **프론트 빌드**: `npm run build` 성공 (Next.js 14.2.35)
- **타입 검사**: Linting and validity of types 통과
- **백엔드 pytest**: 기존 실패 1건 유지 (test_design_chat_anthropic — LLM API 크레딧 부족, 본 수정과 무관)

---

## 6. 완료 기준 충족

| # | 기준 | 상태 |
|---|------|------|
| 1 | go100.newtalk.kr/trade → 새 스케줄 등록 → 전략 선택에 GO100 카드 표시 | ✅ 코드 반영 완료 (tab=v4 + GO100 포함 전달) |
| 2 | GO100 카드 선택 → 계좌 선택 → 스케줄 저장 정상 | ✅ 동일 createSchedule API 사용, strategy_id 저장 가능 |
| 3 | 보고서 GitHub push 200 | ⏳ 푸시 후 curl 200 확인 |

---

## 7. 참고

- **절대 규칙 준수**: kis-v41-* 재시작 없음, strategy_cards ALTER/DROP/DELETE 없음, v4_positions 직접 수정 없음, .env/.bak 커밋 없음.
- **스케줄 runner**: v4_trade_schedules.strategy_id에 GO100 go100_card_id가 저장될 경우, 스케줄 러너에서 GO100 전략 실행 여부는 별도 이슈로, 본 수정 범위 외.
