---
project: KIS
task_id: CUR-V41-CHARTS-CONFIG-001
completed_at: 2026-03-03 20:43 KST
status: completed
exit_code: 0
commit_sha: 9a5f0810
---

## LW Charts v5 차트 UI + desk2_config.yaml 완료

### 생성/수정 파일
| 파일 | 내용 |
|------|------|
| backend/app/routers/v4_desk2_live.py | 283줄, /api/v4/desk/chart/daily 엔드포인트 (캔들+매수매도마커), 다크테마 |
| scripts/desk2/desk2_config.yaml | 가중치/임계값/수수료/지연 등 외부 설정 분리 |

### 커밋: 9a5f0810 — push 완료
