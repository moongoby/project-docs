---
project: KIS
task_id: CUR-V41-DESK2-DB-URL-FIX-001
completed_at: "2026-03-03T12:05:00+09:00"
---

# CUR-V41-DESK2-DB-URL-FIX-001 결과 보고

## 진단

`desk2_realtime_signal.py` 110번 라인에서 `DATABASE_URL` (값: `postgresql+asyncpg://...`) 을
psycopg2.connect()에 직접 전달 → `ProgrammingError: invalid dsn` 발생 확인.

```
psycopg2.ProgrammingError: invalid dsn: missing "=" after
"postgresql+asyncpg://[MASKED_DB_URL]"
```

## 패치 결과

| 파일 | 상태 | 비고 |
|------|------|------|
| desk2_prescoring.py | ✅ 이미 패치됨 | `replace("postgresql+asyncpg://","postgresql://",1)` 존재 |
| desk2_monitor.py | ✅ 이미 패치됨 | 동일 패턴 존재 |
| desk2_auto_trader.py | ✅ 패치 불필요 | SQLAlchemy AsyncSession 사용 |
| desk2_realtime_signal.py | ⚠️ 패치 필요 (root 권한 필요) | /tmp/desk2_realtime_signal_patched.py 로 검증 완료 |

### desk2_realtime_signal.py 수정 내용 (110번 라인)

**Before:**
```python
db_url = db_url or os.environ.get("DATABASE_URL", "dbname=kisautotrade user=kis_admin host=localhost")
conn = psycopg2.connect(db_url)
```

**After (패치본 /tmp/desk2_realtime_signal_patched.py 적용):**
```python
db_url = db_url or os.environ.get("DATABASE_URL_SYNC") or os.environ.get("DATABASE_URL") or ""
db_url = (db_url
          .replace("postgresql+asyncpg://", "postgresql://", 1)
          .replace("postgresql+psycopg2://", "postgresql://", 1)
          ) or "dbname=kisautotrade user=kis_admin host=localhost"
conn = psycopg2.connect(db_url)
```

## 실행 검증

```
INFO __main__ desk2_realtime_signal signal_date=2026-03-03 inserted=0
INSERTED=0
```
→ 오류 없이 실행 완료 (기존 6건 이미 삽입되어 있어 inserted=0)

## DB 확인

```sql
SELECT count(*) FROM v4_desk2_signals WHERE signal_date='2026-03-03';
-- 결과: 6
```

상세:
- T5/307750 FILLED
- T5/027360 FILLED
- T5/001020 FILLED
- S1/054620 FILLED
- S1/322000 FILLED
- S1/105330 FILLED

## 원본 파일 패치 안내 (root 실행 필요)

claudebot은 root:root 소유 파일 직접 수정 불가. 아래 명령을 root에서 실행하세요:

```bash
cp /tmp/desk2_realtime_signal_patched.py /root/kis-autotrade-v4/scripts/desk2/desk2_realtime_signal.py
chown root:root /root/kis-autotrade-v4/scripts/desk2/desk2_realtime_signal.py
chmod 444 /root/kis-autotrade-v4/scripts/desk2/desk2_realtime_signal.py
echo "PATCHED: scripts/desk2/desk2_realtime_signal.py"
```

## 결론

- 오류 원인: `postgresql+asyncpg://` URL이 psycopg2.connect()에 전달됨
- 수정 방향: `DATABASE_URL_SYNC` 우선 사용 + `+asyncpg`/`+psycopg2` strip
- 검증: /tmp 패치본으로 정상 실행 확인
- DB: v4_desk2_signals 2026-03-03 기준 6건 정상 존재
