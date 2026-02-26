# CUR-GO100-R2-INFRA-SETUP — R2 기획서 인프라 사전 준비 완료

**날짜**: 2026-02-26
**코드 레포**: kis-autotrade-v4 (branch: `phase-2c-command-center`)

---

## 0. 인프라 변경 (대표님 직접 수행)

| 항목 | 이전 | 이후 |
|---|---|---|
| 디스크 | `/dev/vda2` 99GB (11GB 여유) | + `/dev/vdb1` 196GB 추가 |
| DB 위치 | `/var/lib/postgresql/16/main` | `/data/postgresql/16/main` (vdb1) |
| DB 디스크 여유 | 11GB | **172GB** |

---

## 1. 테이블 중복 방지 — VIEW 매핑 5건 생성

기획서 R2의 신규 테이블 21건 중 기존 테이블과 중복되는 5건을 VIEW로 매핑하여 데이터 중복 저장 방지.

| VIEW 이름 | 원본 테이블 | 데이터 | 절약 효과 |
|---|---|---|---|
| `go100_minute_bars` | `v4_ohlcv_minute` | 42,615,217행 | ~10GB 중복 방지 |
| `go100_investor_flow` | `v4_investor_daily` | 171,261행 | ~172MB 중복 방지 |
| `go100_tick_data` | `v4_tick_data` | 0행 (스키마 재사용) | 향후 중복 방지 |
| `go100_orderbook_snapshot` | `v4_orderbook_realtime` | 0행 (스키마 재사용) | 향후 중복 방지 |
| `go100_user_profile` | `go100_user_profiles` | 0행 (별칭 통일) | 이름 혼란 방지 |

**총 절약**: ~10.2GB (신규 디스크 172GB 중 6% 보호)

---

## 2. 패키지 설치

| 패키지 | 버전 | 테스트 결과 |
|---|---|---|
| `finance-datareader` | 0.9.102 | KOSPI(KS11) 실데이터 조회 성공 |
| `OpenDartReader` | 0.2.3 | import 성공 (API키 설정 시 사용 가능) |
| 추가 의존성 | lxml 6.0.2, plotly 6.5.2, narwhals 2.17.0 | 충돌 없음 |

**서비스 영향**: go100 백엔드 정상 가동 확인

---

## 3. cron 시간대 분석 및 R2 슬롯 확보

현재 crontab 34건. 장후 16:00~19:30에 14건 밀집.

### R2 신규 스크립트 추가 가능 슬롯

| 시간 | 용도 제안 |
|---|---|
| 16:55 | R2 섹터/업종 분류 수집 |
| 17:20 | R2 글로벌 교차시장 ETF 수집 |
| 17:40 | R2 DART 공시 수집 |
| 18:10 | R2 신용잔고 보강 수집 |
| 19:10 | R2 펀더멘탈 보강 수집 |

---

## 4. 현재 시스템 상태 요약

| 항목 | 상태 |
|---|---|
| DB 디스크 (`/data`) | 172GB 여유 (196GB 중 14GB 사용) |
| 시스템 디스크 (`/`) | 30GB 여유 (99GB 중 65GB 사용) |
| go100 백엔드 | active |
| go100-frontend | active |
| PostgreSQL | active (`/data/postgresql/16/main`) |
| VIEW 매핑 | 5건 생성 완료 |
| 패키지 | FinanceDataReader + OpenDartReader 설치 완료 |

---

## R2 Phase 1 착수 준비 완료 체크리스트

- [x] 디스크 증설 및 DB 이전
- [x] 테이블 중복 방지 VIEW 매핑
- [x] FinanceDataReader 설치 + 실데이터 테스트
- [x] OpenDartReader 설치 (DART API키 설정 필요)
- [x] cron 슬롯 확보 (5개 빈 시간대)
- [ ] DART API키 발급 및 환경변수 등록
- [ ] R2 Phase 1 신규 테이블 16건 생성 (중복 5건 제외)
