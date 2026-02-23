# CUR-GO100-UNIFIED-SAVE-FE 보고서

**작성일:** 2026-02-23  
**작업 지시서:** CUR-GO100-UNIFIED-SAVE-FE  
**목적:** 프론트엔드 경로 정리 + 전략카드 탭 보강 + 채팅위젯 위치 수정 + 전략저장 연동

---

## 1. 백업

- **경로:** `/tmp/backup_UNIFIED_SAVE_FE_<timestamp>.dump` (pg_dump -F c)
- 백업은 STEP 0에서 백그라운드 실행됨.

---

## 2. STEP 1 현재 상태 요약

- **ChatWidget.tsx:** 이미 FAB `fixed bottom-6 right-6 z-50`, 패널 `sm:bottom-24 sm:right-6`. 전체화면 링크만 `/go100/chat` → `/llm`으로 변경.
- **layout.tsx:** ChatWidget은 `<main>` 밖, 동일 레벨에 배치됨. 유지.
- **go100/chat/page.tsx:** 기존 ChatInterface 페이지 → 리다이렉트 페이지로 교체.
- **llm 전략 저장:** `StrategyCardSaveButton` + `ChatMessage`에서 처리. 기존 `createCard`(POST /api/v1/strategy-cards) → `createStrategyCard`(POST /api/go100/strategy-cards)로 변경.
- **전략카드 페이지:** `@/components/strategy/StrategyCard` 사용, catalog API, GO100 토글·검색 이미 존재. 검색 디바운스 300ms 및 URL `tab=my` 지원 추가.
- **StrategyCardDetail:** `/go100/strategies/[id]`에서 사용, GO100 API로 상세 조회. 활성/비활성 토글 및 삭제 버튼 추가.
- **백테스트:** `getBacktestCards` 유지. GO100 카드 옵션 타입 및 선택 시 go100 backtest 실행 분기 추가.

---

## 3. 수정 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/go100/components/ChatWidget.tsx` | 헤더 추가, 전체화면 링크 `/llm`으로 변경 |
| `frontend/src/app/(protected)/layout.tsx` | 헤더 코멘트 추가 |
| `frontend/src/app/(protected)/go100/chat/page.tsx` | 전체 내용 → `/llm` 리다이렉트 페이지로 교체 |
| `frontend/src/components/chat/StrategyCardSaveButton.tsx` | GO100 API 연동(POST /api/go100/strategy-cards), 성공 시 토스트·내 전략 보기 링크, catalog 무효화 |
| `frontend/src/app/(protected)/strategy-cards/page.tsx` | 헤더, 검색 디바운스 300ms, URL `tab=my` 반영 |
| `frontend/src/go100/components/StrategyCardDetail.tsx` | 헤더, 활성/비활성 토글, 삭제 버튼 (updateStrategyCard, deleteStrategyCard) |
| `frontend/src/app/(protected)/backtest/page.tsx` | GO100 카드 타입·선택 분기, "[GO100] 전략명" 표시, 종목 자동 선정 안내, runGo100Backtest·결과 폴링·결과 카드 |
| `frontend/src/go100/api/go100Api.ts` | 헤더 코멘트 추가 |

---

## 4. 빌드 결과

- **tsc --noEmit:** 성공 (exit 0)
- **npm run build:** 성공 (exit 0)

---

## 5. 헬스체크 결과

| 경로 | HTTP 코드 |
|------|-----------|
| /dashboard | 307 (리다이렉트) |
| /strategy-cards | 307 (리다이렉트) |
| /go100 | 200 |
| /llm | 307 (리다이렉트) |
| /go100/chat | 200 |
| /backtest | 200 |

(307은 인증 리다이렉트로 정상.)

---

## 6. 컴플라이언스 체크리스트

- [x] V4.1 핵심 파일 최소 수정 (go100_* 및 지정 FE 파일만 수정)
- [x] .env / .bak 미커밋
- [x] 수정 파일 상단 헤더 코멘트 추가 (CUR-GO100-UNIFIED-SAVE-FE, 2026-02-23)
- [x] /go100/chat → /llm 리다이렉트 확인
- [x] ChatWidget 우하단 위치 유지 (bottom-6 right-6)

---

## 7. 커밋

- **메시지:** `feat: CUR-GO100-UNIFIED-SAVE-FE - 채팅위치 + 경로정리 + 전략저장GO100 + 상세/토글/검색`
- **커밋 해시:** `66b0038f`

---

## 8. 롤백 절차

```bash
sudo systemctl stop go100-frontend
cd /root/kis-autotrade-v4
git revert HEAD --no-edit
sudo systemctl start go100-frontend
sleep 10
curl -s -o /dev/null -w "frontend: %{http_code}\n" http://localhost:3000/go100
```

---

## 9. 참고

- 전략 저장 시 GO100 API body: `strategy_name`, `description`, `source_type: "LLM"`, `entry_rules`/`exit_rules`/`risk_params`/`strategy_params` 등 매핑.
- 백테스트 for-backtest API에서 GO100 카드는 `go100_card_id` 또는 `source: "go100"` 필드로 구분되면 "[GO100] 전략명" 및 GO100 백테스트 실행이 동작함. 백엔드에서 해당 필드 포함 시 정상 노출.
