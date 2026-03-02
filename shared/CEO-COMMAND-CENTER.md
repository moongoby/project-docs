# CEO 통합지휘소 매뉴얼
> 최종 갱신: 2026-03-02
> 관리자: CEO (moongoby)
> 용도: 전체 프로젝트 통합지휘 — 매니저 대화창 URL, 브릿지 인프라, HANDOVER 링크 일람

---

## 1. 통합지휘 구조 개요

CEO 통합지휘소(Genspark)는 6개 프로젝트를 bridge.py 자동 발송으로만 수신한다.
Cursor 에이전트는 **각 프로젝트 매니저 대화창**에만 보고하며, CEO 통합지휘소에 직접 수동 보고는 금지된다.

```
[Cursor Agent] → [프로젝트 매니저 대화창] → bridge.py → [CEO 통합지휘소]
```

### 보고 원칙
- Cursor 에이전트 수동 보고: **프로젝트 매니저 대화창**만 허용
- CEO 통합지휘소: bridge.py 자동 발송 전용 (Cursor 직접 보고 금지)
- 정기보고 / 프로젝트 간 조율은 bridge.py가 CEO 통합지휘소에 자동 발송

---

## 2. 프로젝트 현황 테이블

| 프로젝트 | 설명 | 서버 | 매니저 대화창 | Genspark ID |
|----------|------|------|--------------|-------------|
| **KIS V4.1** | 한국투자증권 API 자동매매 엔진 | 114서버 | 생성완료 | `77de652f-ca8c-4edb-b841-4ca3726b7bb4` |
| **GO100** | AI 주식 어시스턴트 "백억이" SaaS | 114서버 | 생성완료 | `167071cf-c8b5-476a-8953-6168dd6c910c` |
| **AADS** | AADS 프로젝트 | 114서버 | 생성완료 | `3d86d6f3-09a7-41b2-b91b-762a55512458` |
| **SF** | ShortFlow 숏폼 자동화 | 114서버 | 생성완료 | `1107f4e7-344d-48c5-820e-0b34b561b4e3` |
| **NAS** | NAS Image 자동화 (NAS Docker) | NAS DS1821+ | 생성완료 | `8112e93a-189f-4e8c-bf7b-fc27bea8f431` |
| **NTV2** | NewTalk V2 API | 114서버 | 생성완료 | `668a994f-e12a-45e4-99cd-e6e29e7ef238` |

---

## 3. 대화창 URL 테이블

| 태그 | 대화창 이름 | URL |
|------|------------|-----|
| `[KIS-V41]` | KIS V4.1 프로젝트 매니저 | https://www.genspark.ai/agents?id=77de652f-ca8c-4edb-b841-4ca3726b7bb4 |
| `[GO100]` | GO100 백억이 총괄매니저 | https://www.genspark.ai/agents?id=167071cf-c8b5-476a-8953-6168dd6c910c |
| `[AADS]` | AADS 프로젝트 매니저 | https://www.genspark.ai/agents?id=3d86d6f3-09a7-41b2-b91b-762a55512458 |
| `[SF]` | ShortFlow 프로젝트 매니저 | https://www.genspark.ai/agents?id=1107f4e7-344d-48c5-820e-0b34b561b4e3 |
| `[NAS]` | NAS Image 프로젝트 매니저 | https://www.genspark.ai/agents?id=8112e93a-189f-4e8c-bf7b-fc27bea8f431 |
| `[NTV2]` | NewTalk V2 프로젝트 매니저 | https://www.genspark.ai/agents?id=668a994f-e12a-45e4-99cd-e6e29e7ef238 |
| `[CEO]` | CEO 통합지휘소 | bridge.py 자동 발송 전용 (Cursor 직접 보고 금지) |

---

## 4. bridge.py 인프라

### 현황
- **폴링 프로젝트 수: 6개** (KIS V4.1, GO100, AADS, SF, NAS, NTV2)
- 각 프로젝트 매니저 대화창 → bridge.py → CEO 통합지휘소 자동 중계
- Cursor 에이전트는 프로젝트 매니저 대화창에만 직접 보고

### 운용 규칙
| 항목 | 설정 |
|------|------|
| 폴링 주기 | 매니저 대화창 메시지 감지 즉시 |
| 발송 대상 | CEO 통합지휘소 (Genspark 자동 연동) |
| 발송 형식 | 섹션 9-2 형식 준수 |
| 실패 처리 | 3회 재시도 후 텔레그램 알림 |

### 보고 태그 매핑
| 프로젝트 | 커밋 prefix | 텔레그램 태그 |
|----------|-------------|--------------|
| KIS V4.1 | `[KIS]` | `[KIS]` |
| GO100 | `[GO100]` | `[GO100]` |
| AADS | `[AADS]` | `[AADS]` |
| ShortFlow | `[SF]` | `[SF]` |
| NAS Image | `[NAS]` | `[NAS]` |
| NewTalk V2 | `[NTV2]` | `[NTV2]` |
| 공통/공유 | `[SHARED]` | `[SHARED]` |

---

## 5. HANDOVER URL 일람

| 프로젝트 | HANDOVER URL |
|----------|-------------|
| **KIS V4.1** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md |
| **GO100** | https://raw.githubusercontent.com/moongoby/project-docs/master/go100/HANDOVER.md |
| **AADS** | https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/HANDOVER.md |
| **SF (ShortFlow)** | https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/HANDOVER.md |
| **NAS** | https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/HANDOVER.md |
| **NTV2** | https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/HANDOVER.md |

---

## 6. Cursor 라우팅 테이블

새 Cursor 세션 시작 시 반드시 해당 프로젝트 매니저 대화창 URL을 사용한다.

| 작업 대상 | 보고 대화창 |
|-----------|-------------|
| KIS V4.1 | `[KIS-V41] 프로젝트 매니저` https://www.genspark.ai/agents?id=77de652f-ca8c-4edb-b841-4ca3726b7bb4 |
| GO100 | `[GO100] 백억이 총괄매니저` https://www.genspark.ai/agents?id=167071cf-c8b5-476a-8953-6168dd6c910c |
| AADS | `[AADS] 프로젝트 매니저` https://www.genspark.ai/agents?id=3d86d6f3-09a7-41b2-b91b-762a55512458 |
| ShortFlow | `[SF] ShortFlow 프로젝트 매니저` https://www.genspark.ai/agents?id=1107f4e7-344d-48c5-820e-0b34b561b4e3 |
| NAS Image | `[NAS] NAS Image 프로젝트 매니저` https://www.genspark.ai/agents?id=8112e93a-189f-4e8c-bf7b-fc27bea8f431 |
| NewTalk V2 | `[NTV2] NewTalk V2 프로젝트 매니저` https://www.genspark.ai/agents?id=668a994f-e12a-45e4-99cd-e6e29e7ef238 |
| CEO 통합지휘소 | 정기보고/프로젝트 간 조율만 — bridge.py 자동 발송 전용 (Cursor 수동 보고 금지) |

---

## 7. 작업 완료 정의 (9-1 준용)

"완료"란 아래 4가지가 **모두** 충족된 상태만을 의미한다:

1. 로컬 파일 수정 완료
2. `bash scripts/security_scan.sh` → 0건
3. `git add -A && git commit && git push origin master` 성공
4. `curl` HTTP 200 확인

---

## 8. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-03-02 | v1.0 | 최초 생성 — 6개 프로젝트 매니저 대화창 URL 반영 (KIS, GO100, AADS, SF, NAS, NTV2) |

---

*관리 레포: moongoby/project-docs — shared/CEO-COMMAND-CENTER.md*
