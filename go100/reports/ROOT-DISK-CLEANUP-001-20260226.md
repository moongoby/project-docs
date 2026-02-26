# ROOT-DISK-CLEANUP-001-20260226

**제목**: 루트 디스크 정리 (PostgreSQL 원본 삭제 및 캐시 정리)  
**일자**: 2026-02-26  
**유형**: 운영 정리

---

## 1. 개요

- 루트(/) 사용률 90% 상태에서 디스크 여유 확보를 위해 검증 후 원본 PostgreSQL 디렉터리 삭제 및 로그·캐시 정리 수행.
- DB는 이미 `/data/postgresql/16/main`(data_directory)에서 동작 중이므로 `/var/lib/postgresql/`은 미사용 원본.

---

## 2. 1단계 — 검증 (삭제 전)

| 항목 | 결과 |
|------|------|
| **DB 크기** | `pg_size_pretty(pg_database_size('kisautotrade'))` → **14 GB** |
| **go100_news_items 건수** | **288,787건** (`psql -d kisautotrade -c "SELECT count(*) FROM go100_news_items;"`) |

- DB가 `/data`에서 정상 동작함을 확인한 뒤에만 삭제 진행.

---

## 3. 2단계 — 원본 DB 디렉토리 크기

| 경로 | 크기 |
|------|------|
| `/var/lib/postgresql/` | **14G** |

---

## 4. 3단계 — 원본 삭제

- `rm -rf /var/lib/postgresql/` 실행 완료 (에러 없음).

---

## 5. 4단계 — 추가 정리

| 조치 | 결과 |
|------|------|
| **journalctl --vacuum-size=100M** | 약 **378.6MB** 정리 |
| **apt-get clean / autoremove -y** | 실행 완료 (제거 패키지 0개) |
| **/tmp/*, /var/tmp/\*** | `sudo rm -rf` 실행 완료 |

---

## 6. 5단계 — 최종 디스크 사용률

| 파일시스템 | 크기 | 사용 | 가용 | 사용률 |
|------------|------|------|------|--------|
| /dev/vdb1 | 196G | 14G | 172G | **8%** (/data) |
| /dev/vda2 | 99G | 65G | 30G | **69%** (/) |

**루트(/) 사용률 변화: 90% → 69%** (약 19GB 확보)

---

## 7. 문서 레포 푸시 경로

- **v4.1 (kis-autotrade-v4)**: `project-docs/kis-autotrade-v4/reports/ROOT-DISK-CLEANUP-001-20260226.md`
- **go100**: `project-docs/go100/reports/ROOT-DISK-CLEANUP-001-20260226.md`
- **원본 보고서**: `kis-autotrade-v4/report/v41/ROOT-DISK-CLEANUP-001-20260226.md`
