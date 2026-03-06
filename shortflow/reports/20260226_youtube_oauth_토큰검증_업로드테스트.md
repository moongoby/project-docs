# YouTube OAuth 토큰 검증 및 업로드 테스트 보고서

**일시:** 2026-02-26 KST  
**서버:** ssh root@114.207.244.86  
**작업 디렉터리:** /data/shortflow  
**주의:** 토큰 재발급 없이 검증·업로드 테스트만 수행.

---

## STEP 1 — 토큰 파일 확인

| 파일 | 존재 | 유효성 |
|------|------|--------|
| `config/youtube_token_economy.json` | ✅ 존재 (778B, 2026-02-26 12:02) | ✅ JSON 유효, token/refresh_token/client_id 등 필드 있음 |
| `config/youtube_token_health.json` | ✅ 존재 (778B, 2026-02-26 12:04) | ✅ JSON 유효, token/refresh_token/client_id 등 필드 있음 |

- economy: 3분경제 채널용 OAuth 토큰
- health: 건강한입 채널용 OAuth 토큰

---

## STEP 2 — .gitignore 확인

- `config/youtube_token_*.json`, `.env`, `.env.*`, `venv/`, `.venv/` 모두 포함됨.
- **누락 항목 없음. 추가 작업 없음.**

---

## STEP 3 — 업로드 테스트 (economy, 3분경제)

| 항목 | 값 |
|------|-----|
| **결과** | ✅ 성공 |
| **Video ID** | `ZwysqK_puMY` |
| **URL** | https://youtube.com/shorts/ZwysqK_puMY |
| **privacy 상태** | `private` |
| **업로드 파일** | `output/videos/economy/20260225_122907_economy.mp4` |
| **에러 메시지** | 없음 |

---

## STEP 4 — 업로드 테스트 (health, 건강한입)

| 항목 | 값 |
|------|-----|
| **결과** | ✅ 성공 |
| **Video ID** | `nZkJ9PjviH4` |
| **URL** | https://youtube.com/shorts/nZkJ9PjviH4 |
| **privacy 상태** | `private` |
| **업로드 파일** | `output/videos/health/20260225_122918_health.mp4` |
| **에러 메시지** | 없음 |

---

## STEP 5 — SaaS 대시보드 복구

| 항목 | 상태 |
|------|------|
| **컨테이너** | `docker start shortflow-saas-dashboard` 실행 후 정상 기동 |
| **docker ps** | `shortflow-saas-dashboard` Up, 0.0.0.0:3001->3000/tcp |
| **HTTP 응답** | `curl -s -o /dev/null -w "%{http_code}" http://localhost:3001` → **200** |

---

## 요약

- **토큰:** economy/health 토큰 파일 존재·유효, 재발급 미수행.
- **업로드:** economy·health 모두 비공개(private) 업로드 성공.
- **대시보드:** shortflow-saas-dashboard 컨테이너 기동, localhost:3001 응답 200.
- **에러:** 전체 단계에서 에러 없음. (Python 3.8 EOL 관련 FutureWarning만 출력됨)

---

## 보안 준수 사항

- `config/youtube_token_*.json`, `.env`, `venv/` — git 커밋하지 않음.
- 업로드는 모두 비공개(private)로 수행됨.
