# GO100 인수인계서
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 1. 프로젝트 개요
- GO100: AI 기반 주식 자동매매 SaaS. AI 전략 설계(백억이), 전략카드, 백테스트, 자동매매. V4.1 코드베이스 공유. (기획서 docs/PLANNING.md 참조)

## 2. 접속 정보
- **서버**: root@kis-autotrade-v4
- **DB**: kisautotrade / kis_admin / **** (비밀번호 문서 비기재)
- **GitHub**: moongoby/go100 (private), 브랜치 phase-2c-command-center
- **도메인**: go100.newtalk.kr, trading41.newtalk.kr
- **project-docs**: moongoby/project-docs (Public GitHub)

## 3. 계정
- moongoby@naver.com: v4_users.user_id=3 (GO100 카드 13,14,15 소유)
- moongoby@gmail.com: v4_users.user_id=2
- legacy users.id 15 → v4 user_id 3, legacy 6 → v4 2. get_effective_uid() 사용 필수.

## 4. 서비스 관리 명령
- **백엔드**: sudo systemctl restart go100 (localhost:8002)
- **프론트**: sudo systemctl restart go100-frontend (localhost:3000)
- **빌드**: cd /root/kis-autotrade-v4/frontend && npm run build
- **헬스**: curl http://localhost:8002/health

## 5. 작업 규칙
1. go100_* 파일/테이블만 수정.
2. 모든 수정 파일에 헤더 코멘트 (작업ID, 날짜).
3. .env, .bak 커밋 금지.
4. DB 스키마 변경은 go100_* 한정.
5. 백업→확인→수정→빌드→재시작→검증→커밋→보고서→문서 갱신.

## 6. 현재 상태 (2026-02-23)
### 완료 항목 (git log 기반)
- 문서 체계 구축 (CONTEXT, architecture/handover/plan 정리)
- CUR-GO100-HOTFIX-IMPORT (strategy_router import 누락 수정)
- CUR-GO100-HOTFIX-CRITICAL (전략저장 fallback, 상세모달, 토글API, 채팅 z-index)
- BT-ENGINE-UPGRADE (entry/exit datetime, MFE/MAE, regime, strategy_name, commission)
- CUR-GO100-UNIFIED-SAVE-BE/FE (전략저장 go100 통일, AI 자동전략명, user_utils)
- CUR-GO100-MY-STRATEGY-FIX, CUR-GO100-CARD-DETAIL-FIX, CUR-GO100-CARD-REDESIGN-BE/FE
- CUR-GO100-CHAT-WIDGET, GO100 Catalog 병합, 전략카드 탭 tab=all/my

### 미해결 이슈
- docs/ISSUES.md 참조 (채팅 위젯 미표시, 백테스트 드롭다운 미검증, 전략 저장 E2E 미검증 등)

### 잔여 로드맵
- docs/ROADMAP.md 참조 (Phase 2 안정화 5개, Phase 3 고도화, Phase 4 런칭)

## 7. 주의사항
- user_id 매핑 필수: get_effective_uid() 사용.
- DB명 실제: kisautotrade (인계 문서의 go100db 아님).
- PK: go100_strategy_cards.go100_card_id (id 아님).
