# GO100-V5-P2-9: 경로 마이그레이션 — 사이트맵 URL 리다이렉트 10개

## 요약
사이트맵 URL과 실제 경로가 다른 페이지들의 리다이렉트 처리. 10개 경로에 Next.js `redirect()` 기반 page.tsx 생성.

## 인계 확인
```
직전 완료: GO100-V5-P2-8 (자동매매 실행 로그 페이지)
현재 단계: Phase 2 (기능 개발/리다이렉트)
CEO 지시 적용: D-001, D-007, PATH-001
strategy_cards: 60+
open_positions: 0
```

## 변경 내용

### 생성된 리다이렉트 파일 (10개)

| 경로 | 리다이렉트 대상 | 파일 위치 |
|------|----------------|----------|
| /ai/chat | /llm | frontend/src/app/ai/chat/page.tsx |
| /stocks/[code] | /stock/${code} | frontend/src/app/stocks/[code]/page.tsx |
| /strategies | /go100/strategies | frontend/src/app/strategies/page.tsx |
| /trading/paper | /go100/paper-trading | frontend/src/app/trading/paper/page.tsx |
| /trading/live | /go100/live-trading | frontend/src/app/trading/live/page.tsx |
| /trading/auto | /trade | frontend/src/app/trading/auto/page.tsx |
| /monitor/system | /monitoring | frontend/src/app/monitor/system/page.tsx |
| /legal/terms | /terms | frontend/src/app/legal/terms/page.tsx |
| /legal/privacy | /privacy | frontend/src/app/legal/privacy/page.tsx |
| /feed/news | /go100/feed | frontend/src/app/feed/news/page.tsx |

### 구현 상세
- **패턴**: Next.js `redirect()` 함수 (server component)
- **각 파일**: 3~5줄 (import + function export + redirect call)
- **동적 경로**: `/stocks/[code]` → 매개변수 처리로 `props.params.code` 활용
- **정적 경로**: 9개 경로는 고정 리다이렉트

### 코드 예시
```typescript
import { redirect } from "next/navigation";

export default function AiChatRedirect() {
  redirect("/llm");
}
```

## 검증 결과
- ✅ 10개 파일 모두 생성 완료
- ✅ 문법 검증: TypeScript 구문 정상
- ✅ 동적 경로 처리: props.params 기반 URI 구성
- ✅ 기존 리다이렉트 패턴 준수 (go100/page.tsx, go100/notifications/page.tsx 참조)
- ✅ middleware.ts와 충돌 없음 (미들웨어는 전략/전전 리다이렉트, page는 페이지 레벨 리다이렉트)

## 다음 단계
1. 빌드 검증: `npm run build` 실행 (Runner 담당)
2. 배포: 코드 레포 push → Runner 자동 빌드/배포
3. 사이트맵 URL 테스트 (각 경로 접근 → 리다이렉트 확인)

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-PATH-MIGRATION-REDIRECTS-001-20260420.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-PATH-MIGRATION-REDIRECTS-001-20260420.md
- HTTP 확인: (push 후 검증)
- HANDOVER 업데이트: (완료 예정)
