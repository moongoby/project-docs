# GO100 인수인계서 — 3계층 인덱스
> 최종 업데이트: 2026-04-07 | v18.0 (3계층 전환)

**운영 메모 (2026-04-07):** GO100 배치·가설 데몬 실행 Python을 **`.venv` → `venv` 통일**(P0). 비동기 DB 풀 **8+4**(P1). 코드 커밋 `63d1473ccab339542b67814a17bf309b3f6ed6e4` — 상세 [CUR-GO100-P0P1-EXEC-001-20260407.md](reports/CUR-GO100-P0P1-EXEC-001-20260407.md). 서버 **crontab·systemd**는 로컬 적용 별도.

이 파일은 인덱스입니다. 상세 내용은 아래 3계층 파일을 참조하세요.

---

## 계층 구조

| 계층 | 파일 | 내용 | 줄수 |
|------|------|------|------|
| L1 | [handover/HANDOVER.md](handover/HANDOVER.md) | 현재 상태, 즉시 체크리스트, 다음 작업 | ~50 |
| L2 | [handover/HANDOVER-DETAIL.md](handover/HANDOVER-DETAIL.md) | 완료 작업 테이블, 아키텍처, DB, 파일 경로 | ~200 |
| L3 | [handover/HANDOVER-ARCHIVE.md](handover/HANDOVER-ARCHIVE.md) | 과거 완료 작업 전체, 버전 이력, Known Issues | 나머지 |

---

## 빠른 시작

새 대화창에서는 **L1 파일**을 먼저 읽으세요:
```
/root/project-docs/go100/handover/HANDOVER.md
```

---

> 이전 단일 파일(v17.0): 백업 → `go100/HANDOVER.md.bak.v17.0-archive`
