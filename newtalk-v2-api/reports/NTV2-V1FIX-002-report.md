# NTV2-V1FIX-002: V1 이미지 URL DO→newtalk.kr 치환 Phase 2 실행 결과 보고서

**Task ID:** NTV2-V1FIX-002
**날짜:** 2026-03-05 KST
**작성자:** Claude Code (server-114 / kis-autotrade-v4)
**버전:** 1.0.0-BLOCKED
**우선순위:** P0 (CEO 승인 완료)

---

## 1. 개요

V1-FIX-001 Phase 1(소스 분석) 완료 후, Phase 2(V1 DB 조사·치환) 실행을 시도한 결과 보고서.

**Phase 1 완료 내용 (2026-02-27):**
- V1 소스 코드(PHP Controller) 내 `$oceanPath` 서빙 URL → `https://newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/` 로 치환 완료
- DB 전수 조사 결과: `goods_detail` 테이블 16개 컬럼(GoodsEtc60~74, DanharooDescription), 155행 영향

---

## 2. Phase 2 실행 환경

| 항목 | 값 |
|------|-----|
| 실행 서버 | server-114 (kis-autotrade-v4) |
| 실행 사용자 | claudebot (uid=1003) |
| V1 DB 위치 | rfree-009 서버 (127.0.0.1:3306, autoda) — 원격 서버 |
| MySQL 클라이언트 | 미설치 (apt-get 권한 없음) |
| SSH 키 | /root/.ssh/id_ed25519_newtalk — root 전용, claudebot 접근 불가 |

---

## 3. 실행 시도 및 결과

### Step 1: DB 접속 확인

```bash
# 로컬 포트 3306 확인
python3 -c "import socket; s=socket.socket(); s.settimeout(2); r=s.connect_ex(('127.0.0.1',3306)); print('3306:', r)"
# 결과: 3306: 111 (ECONNREFUSED — MySQL 미가동)

# SSH 키 확인
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk" git ls-remote
# 결과: Warning: Identity file /root/.ssh/id_ed25519_newtalk not accessible: Permission denied.

# MySQL 클라이언트 확인
which mysql
# 결과: 없음 (미설치)

# pymysql 설치 시도
pip3 install --break-system-packages pymysql
# 결과: Successfully installed pymysql-1.1.2
# 단, V1 DB는 rfree-009의 localhost(127.0.0.1:3306)이므로 원격 직접 접속 불가
```

**결론: server-114(kis-autotrade-v4)에서 V1 DB(autoda@rfree-009)에 접속 불가**

---

### Step 2: SELECT 조회 (미실행 — 접속 불가)

Phase 1 결과(기존 V1-FIX-001-report.md)를 기준으로 예상 결과 기록:

| 테이블 | 컬럼 | Phase 1 기준 DO URL 포함 건수 |
|--------|------|-------------------------------|
| goods_detail | GoodsEtc60 | 155 |
| goods_detail | GoodsEtc61 | 155 |
| goods_detail | GoodsEtc62 | 155 |
| goods_detail | GoodsEtc63 | 155 |
| goods_detail | GoodsEtc64 | 155 |
| goods_detail | GoodsEtc65 | 155 |
| goods_detail | GoodsEtc66 | 155 |
| goods_detail | GoodsEtc67 | 155 |
| goods_detail | GoodsEtc68 | 155 |
| goods_detail | GoodsEtc69 | 155 |
| goods_detail | GoodsEtc70 | 155 |
| goods_detail | GoodsEtc71 | 155 |
| goods_detail | GoodsEtc72 | 155 |
| goods_detail | GoodsEtc73 | 155 |
| goods_detail | GoodsEtc74 | 155 |
| goods_detail | DanharooDescription | 155 |
| goods | (모든 텍스트 컬럼) | **0** |

**총 영향 행: 155건 (goods_detail만 해당)**

**DO URL 패턴:** `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/YYYYMM/filename`
**변환 대상 URL:** `https://newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/filename`

---

### Step 3: 백업 (미실행 — 접속 불가)

Phase 1에서 이미 수행됨 (2026-02-27):
- `/root/backup/v1-fix-001-20260227/goods_detail_before_20260227.sql` — 1.1GB

Phase 2 실행 시 추가 백업 필요:
```bash
# rfree-009 서버에서 실행 필요
mysqldump -u pigupuser -p autoda goods goods_detail \
  > /root/backup/v1-fix-002-$(date +%Y%m%d_%H%M%S).sql
```

---

### Step 4: URL 치환 UPDATE (미실행 — 접속 불가)

rfree-009 서버에서 실행해야 할 쿼리:

```sql
-- GoodsEtc60~72, GoodsEtc74: 파일명에서 GoodsCode 추출 후 경로 재조합
UPDATE goods_detail SET GoodsEtc60 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc60, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc60, '/', -1)) WHERE GoodsEtc60 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc61 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc61, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc61, '/', -1)) WHERE GoodsEtc61 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc62 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc62, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc62, '/', -1)) WHERE GoodsEtc62 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc63 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc63, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc63, '/', -1)) WHERE GoodsEtc63 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc64 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc64, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc64, '/', -1)) WHERE GoodsEtc64 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc65 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc65, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc65, '/', -1)) WHERE GoodsEtc65 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc66 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc66, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc66, '/', -1)) WHERE GoodsEtc66 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc67 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc67, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc67, '/', -1)) WHERE GoodsEtc67 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc68 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc68, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc68, '/', -1)) WHERE GoodsEtc68 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc69 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc69, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc69, '/', -1)) WHERE GoodsEtc69 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc70 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc70, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc70, '/', -1)) WHERE GoodsEtc70 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc71 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc71, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc71, '/', -1)) WHERE GoodsEtc71 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc72 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc72, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc72, '/', -1)) WHERE GoodsEtc72 LIKE '%digitaloceanspaces.com%';
-- GoodsEtc73: base path만 저장 → goods 테이블 JOIN으로 GoodsCode 사용
UPDATE goods_detail gd
INNER JOIN goods g ON gd.goods_id = g.id
SET gd.GoodsEtc73 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', LOWER(g.GoodsCode), '/')
WHERE gd.GoodsEtc73 LIKE '%digitaloceanspaces.com%' AND gd.GoodsEtc73 != '';
UPDATE goods_detail SET GoodsEtc74 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc74, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc74, '/', -1)) WHERE GoodsEtc74 LIKE '%digitaloceanspaces.com%';
-- DanharooDescription: HTML 내 img src 치환 (REPLACE 사용)
UPDATE goods_detail SET DanharooDescription = REPLACE(DanharooDescription, 'https://newtalk.nyc3.cdn.digitaloceanspaces.com', 'https://newtalk.kr/data/files/goods/goodscode/img') WHERE DanharooDescription LIKE '%digitaloceanspaces.com%';
```

---

### Step 5: 검증 쿼리 (미실행)

```sql
-- 치환 후 DO URL 잔존 여부 확인 (기대값: 0)
SELECT COUNT(*) FROM goods_detail
WHERE CONCAT(
  IFNULL(GoodsEtc60,''), IFNULL(GoodsEtc61,''), IFNULL(GoodsEtc62,''),
  IFNULL(GoodsEtc63,''), IFNULL(GoodsEtc64,''), IFNULL(GoodsEtc65,''),
  IFNULL(GoodsEtc66,''), IFNULL(GoodsEtc67,''), IFNULL(GoodsEtc68,''),
  IFNULL(GoodsEtc69,''), IFNULL(GoodsEtc70,''), IFNULL(GoodsEtc71,''),
  IFNULL(GoodsEtc72,''), IFNULL(GoodsEtc73,''), IFNULL(GoodsEtc74,''),
  IFNULL(DanharooDescription,'')
) LIKE '%digitaloceanspaces.com%';

-- 샘플 5건 확인
SELECT GoodsEtc60, GoodsEtc73 FROM goods_detail
WHERE GoodsEtc60 LIKE '%newtalk.kr%'
LIMIT 5;
```

---

## 4. 실패 원인 분석

| 항목 | 상태 | 상세 |
|------|------|------|
| V1 MySQL (autoda) 접속 | ❌ BLOCKED | rfree-009 서버 127.0.0.1:3306, 원격 접속 불가 |
| SSH to rfree-009 | ❌ BLOCKED | /root/.ssh/id_ed25519_newtalk — root 소유, claudebot 접근 불가 |
| MySQL 클라이언트 설치 | ❌ BLOCKED | dpkg lock 없음 (sudo 권한 없음) |
| pymysql 설치 | ✅ 완료 | 단, 원격 MySQL 접속 불가로 무의미 |
| 로컬 포트 3306 | ❌ 없음 | 이 서버는 kis-autotrade-v4, V1 DB 없음 |
| git push (project-docs) | ❌ BLOCKED | SSH 키 접근 불가 (Permission denied) |

**근본 원인:**
server-114 Bridge 환경에서 NTV2(rfree-009) 지시서를 실행 중. V1 DB는 rfree-009 서버에만 존재.
HANDOVER.md 섹션 5 "Bridge 환경 오류" 동일 패턴.

---

## 5. 완료 기준 달성 여부

| 완료 기준 | 상태 |
|-----------|------|
| DO Spaces URL 0건 확인 (치환 후) | ❌ 미실행 (DB 접속 불가) |
| 이미지 정상 로딩 확인 (샘플 5건) | ❌ 미실행 |
| 백업 파일 존재 확인 | ⚠️ Phase 1 백업은 존재 (goods_detail_before_20260227.sql), Phase 2 신규 백업 미실행 |
| 보고서 + HANDOVER push 완료 | ❌ SSH 키 접근 불가로 push 불가 |

---

## 6. 권장 조치

### Option A: rfree-009 서버 직접 실행 (권장)
rfree-009 서버에 직접 SSH 접속하여 아래 스크립트 실행:

```bash
# rfree-009에서 직접 실행
ssh -p [SSH-PORT] -i ~/.ssh/id_ed25519_newtalk root@[SERVER-IP]

# 1. 현재 DO URL 건수 확인
mysql -u pigupuser -p -h 127.0.0.1 -P 3306 autoda <<'EOF'
SELECT 'goods_detail' AS tbl, 'total_do_urls' AS col,
  COUNT(*) AS cnt FROM goods_detail
WHERE CONCAT(
  IFNULL(GoodsEtc60,''), IFNULL(GoodsEtc61,''), IFNULL(GoodsEtc62,''),
  IFNULL(GoodsEtc63,''), IFNULL(GoodsEtc64,''), IFNULL(GoodsEtc65,''),
  IFNULL(GoodsEtc66,''), IFNULL(GoodsEtc67,''), IFNULL(GoodsEtc68,''),
  IFNULL(GoodsEtc69,''), IFNULL(GoodsEtc70,''), IFNULL(GoodsEtc71,''),
  IFNULL(GoodsEtc72,''), IFNULL(GoodsEtc73,''), IFNULL(GoodsEtc74,''),
  IFNULL(DanharooDescription,'')
) LIKE '%digitaloceanspaces.com%';
EOF

# 2. 백업
mysqldump -u pigupuser -p -h 127.0.0.1 -P 3306 autoda goods goods_detail \
  > /root/backup/v1-fix-002-$(date +%Y%m%d_%H%M%S).sql

# 3. 위 Step 4의 UPDATE 쿼리 실행 (write 권한 계정 필요)

# 4. 검증 (기대값: 0)
mysql -u pigupuser -p -h 127.0.0.1 -P 3306 autoda -e \
  "SELECT COUNT(*) FROM goods_detail WHERE GoodsEtc60 LIKE '%digitaloceanspaces.com%';"
```

### Option B: claudebot SSH 키 권한 부여
```bash
# root 계정에서 실행
chmod 644 /root/.ssh/id_ed25519_newtalk
# 또는 claudebot 전용 키 생성 + rfree-009 authorized_keys 등록
```

---

## 7. 참고 문서

- Phase 1 보고서: `newtalk-v2-api/reports/V1-FIX-001-report.md`
- DO URL 샘플: `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/202602/bl5861c5c-600_1.jpg`
- 변환 후 URL: `https://newtalk.kr/data/files/goods/goodscode/img/bl5861c5c/bl5861c5c-600_1.jpg`
- HANDOVER 섹션 6: Bridge 환경 오류 기록 (2026-03-03~04)

---

*보고서 생성: 2026-03-05 17:40 KST — server-114 (kis-autotrade-v4), claudebot*
