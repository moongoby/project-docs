# CLAUDE.md — 211서버 멀티 프로젝트 공통 규칙

## 프로젝트 식별
- 작업 지시에 "GO100" 포함 → .cursor/rules/go100-rules.md 적용
- 작업 지시에 "KIS" 또는 "V4.1" 포함 → .cursor/rules/kis-v41-rules.md 적용
- 불명확할 경우 → 반드시 사용자에게 확인 후 진행

## 서버 공통 정보
- 서버: root@kis-autotrade-v4
- 프로젝트 루트: /root/kis-autotrade-v4
- DB: PostgreSQL kisautotrade / kis_admin / localhost:5432
- 백엔드: FastAPI localhost:8002 (systemd go100)
- 프론트: Next.js localhost:3000 (systemd go100-frontend)
- Python 3.12.3, Node v18.19.1

## 공유 테이블 (양쪽 프로젝트 공통)
- v4_users (4행): 사용자 인증/매핑
- accounts (7행): 증권 계좌
- users (12행): 레거시 사용자 (JWT 토큰 소스)
★ user_id 매핑: legacy users.id ≠ v4_users.user_id, 반드시 get_effective_uid() 사용

## 공유 파일 (수정 시 양쪽 영향도 확인 필수)
- backend/app/main.py (라우터 등록)
- backend/app/services/strategy_card_service.py (catalog V4+GO100 병합)
- frontend/src/app/(protected)/strategy-cards/page.tsx
- frontend/src/app/(protected)/backtest/page.tsx
- frontend/src/app/(protected)/layout.tsx

## 공통 절대 규칙
1. .env, .bak 파일 절대 커밋 금지
2. 작업 전 DB 백업: pg_dump -h localhost -U kis_admin -d kisautotrade -F c -f /tmp/backup_<TASK>_$(date +%Y%m%d_%H%M%S).dump
3. 작업 후 빌드 검증: npm run build 후 BUILD_ID 시간 > 커밋 시간 확인
4. 서비스 재시작: sudo systemctl restart go100 && sudo systemctl restart go100-frontend
5. 헬스체크: curl http://localhost:8002/health && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/go100
