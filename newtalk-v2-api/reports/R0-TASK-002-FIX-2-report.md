# R0-TASK-002-FIX-2 작업 보고서

**문서번호**: NT-V2-R0-TASK-002-FIX-2  
**작성일**: 2026-02-21  
**대상**: Cursor AI (지시서 NT-V2-R0-TASK-002-FIX-2)

### 실행 순서 (서버 기준)

1. **STEP 1** (표님): SSH 접속 → V1 `database.php` 경로 탐색 → 비밀번호 확인·접속 테스트. (비밀번호는 Git·보고서에 기록 금지)
2. **STEP 2~4**: 서버에서 `export DBPW='<비밀번호>' && /srv/newtalk-v2/docs/scripts/R0-TASK-002-FIX-2-runbook.sh` 실행.  
   또는 지시서 4·5·6절 명령을 수동 실행 후 본 보고서 3·4·5절 표를 채움.
3. **보고서 보강**: 3.1, 3.2, 4.3, 5, 6절의 (서버 실행 후 기입) 란을 실제 결과로 채움.

---

## 1. 작업 요약

| 항목 | 담당 | 상태 |
|------|------|------|
| STEP 1: V1 DB 비밀번호 확인 | 표님 (서버 접속 후 수동) | 서버에서 실행 |
| STEP 2: V1 실측 스키마 추출 | 런북 스크립트 | 스크립트 제공 완료 |
| STEP 3: Git "unknown option trailer" 해결 | 런북 + 본 보고서 가이드 | 진단·해결 방법 문서화 |
| STEP 4: GitHub 푸시 | 런북 스크립트 | 저장소 존재 시 실행 |

---

## 2. STEP 1: V1 DB 비밀번호 확인 방법 (경로만, 비밀번호 미기록)

- **접속**: `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86`
- **V1 DB 설정 파일 탐색 명령 (읽기만, 수정 금지)**  
  - `find /home -name "database.php" -path "*/config/*" 2>/dev/null`  
  - `find /var/www -name "database.php" -path "*/config/*" 2>/dev/null`  
  - `find / -name "database.php" -path "*/autoda/*" 2>/dev/null | head -10`
- **확인 방법**: 찾은 경로에서  
  `cat <경로>/database.php | grep -A5 "password\|hostname\|username\|database"`  
  → CodeIgniter 형식이면 `$db['default']['password']` 등으로 비밀번호 확인.
- **접속 테스트 (비밀번호는 보고서·Git에 기록 금지)**  
  `mysql -u pigupuser -p'<비밀번호>' -h 127.0.0.1 -P 3306 autoda -e "SELECT 1;"`  
  → 성공 시 STEP 2 실행 가능.

**비밀번호를 찾지 못한 경우**: 위 find 결과 경로만 보고서에 기록하고, 표님께 경로 전달 후 비밀번호 확인 요청.

---

## 3. STEP 2: V1 실측 스키마 추출 결과

서버에서 아래 중 하나로 실행한 뒤, 아래 표를 채우면 됨.

- **방법 A**: `export DBPW='<비밀번호>' && /srv/newtalk-v2/docs/scripts/R0-TASK-002-FIX-2-runbook.sh`
- **방법 B**: 지시서 4절의 mysql/mysqldump 명령을 직접 실행 (출력 경로: `/srv/newtalk-v2/docs/`)

### 3.1 추출 파일 및 수치 (서버 실행 후 기입)

| 항목 | 값 | 비고 |
|------|-----|------|
| v1-tables-overview.tsv | (행 수) | `wc -l docs/v1-tables-overview.tsv` |
| v1-columns-detail.tsv | (행 수) | `wc -l docs/v1-columns-detail.tsv` |
| v1-indexes.tsv | (행 수) | `wc -l docs/v1-indexes.tsv` |
| v1-schema-full.sql | (파일 크기) | `ls -lh docs/v1-schema-full.sql` |
| 테이블 수 | (개) | overview 행 수 - 1(헤더) |
| 컬럼 수 | (개) | columns-detail 행 수 - 1(헤더) |

### 3.2 핵심 테이블 DESCRIBE vs V2 마이그레이션 대조

서버에서 다음 실행 결과를 보관하고, 누락 컬럼이 있으면 아래에 기록.

```bash
mysql -u pigupuser -p"$DBPW" -h 127.0.0.1 -P 3306 autoda -e "
  DESCRIBE users;
  DESCRIBE goods;
  DESCRIBE goods_master;
  DESCRIBE order_product;
  DESCRIBE order_block_detail;
  DESCRIBE order_barcode;
"
```

| V1 테이블 | V2 대응 | 대조 결과 (서버 실행 후 기입) |
|-----------|---------|------------------------------|
| users | users (2026_02_21_100001 추가 컬럼) | V2: phone, company_name, business_number, v1_idx, v1_auth_code, deleted_at 추가. V1 컬럼 중 미매핑 있으면 기록. |
| goods | products | V1 goods → V2 products. v1_goods_idx 등 보존 여부 확인. |
| goods_master | product_channels 등 | V1 master → V2 product 관련 테이블 매핑 확인. |
| order_product | orders, order_items | V1 order_product 컬럼이 V2 orders/order_items에 반영되었는지 확인. |
| order_block_detail | purchase_order_items 등 | 매핑 확인. |
| order_barcode | barcodes | 매핑 확인. |

**누락 컬럼 발견 시**: 긴급 수정이 필요하면 마이그레이션 추가 파일 생성 후 보고서에 파일명·내용 요약 기록.

---

## 4. STEP 3: Git "unknown option trailer" 오류 원인 및 해결

### 4.1 원인 진단 (서버에서 실행)

```bash
cd /srv/newtalk-v2
git --version
git config --global --get-regexp alias
git config --local --get-regexp alias
git config --global --get-regexp commit
git config --local --get-regexp commit
git config --system --list 2>/dev/null | grep -iE 'commit|trailer'
env | grep -i GIT
```

- **가능한 원인 A**: `commit.trailer` 등 trailer 관련 설정이 있음.  
  → `git config --global --unset commit.trailer` (또는 해당 키) 실행.
- **가능한 원인 B**: Git 버전이 낮아 특정 옵션 미지원.  
  → `git --version` 결과를 보고서에 기록. 2.25 이하일 경우 업그레이드 권장.
- **가능한 원인 C**: 환경변수 `GIT_TRAILER_TOKEN` 등이 설정됨.  
  → `unset GIT_TRAILER_TOKEN` (필요 시 기타 GIT_* 변수 제거).
- **가능한 원인 D**: 글로벌 hook 또는 template에 trailer 로직 포함.  
  → `git config --global init.templateDir` 확인 후, 해당 template 내 commit-msg 등 검사.

### 4.2 해결 방법

1. **진단 결과 반영**: 위 명령 출력에서 trailer/commit 관련 항목이 있으면 제거.
2. **우회 커밋 (R0-TASK-001 동일)**:  
   `env -i HOME="$HOME" PATH="/usr/bin:/bin" git add -A`  
   `env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "[R0-002] feat: ..."`  
   → 환경·config 영향을 제거한 상태로 커밋.
3. **일괄 실행**: `docs/scripts/R0-TASK-002-FIX-2-runbook.sh`가 일반 commit 실패 시 자동으로 `env -i` 우회 커밋을 시도함.

### 4.3 진단 결과 (서버 실행 후 기입)

| 항목 | 결과 |
|------|------|
| git --version | (기입) |
| commit/trailer 관련 config | (있음/없음, 키 목록) |
| GIT_* 환경변수 | (있음/없음) |
| 적용한 조치 | (unset / env -i 우회 / 기타) |
| 최종 커밋 성공 여부 | (예/아니오) |

---

## 5. STEP 4: GitHub 푸시 결과

서버에서 실행:

```bash
ssh -T git@github.com 2>&1
git ls-remote origin 2>&1
git push -u origin main
git push -u origin develop
git push -u origin feature/R0-TASK-002-db-design
```

| 항목 | 결과 (서버 실행 후 기입) |
|------|---------------------------|
| SSH 연결 (github.com) | (성공/실패) |
| origin 저장소 | (있음/없음, "Repository not found" 시 대표님 요청) |
| main 푸시 | (성공/실패/해당 없음) |
| develop 푸시 | (성공/실패/해당 없음) |
| feature/R0-TASK-002-db-design 푸시 | (성공/실패/해당 없음) |

---

## 6. V1 영향 없음 확인

- **원칙**: V1 소스(/home/autoda/ 등) 수정 금지, V1 DB(autoda) SELECT만 허용.
- **확인 (선택)**: 스키마 추출·마이그레이션 작업은 모두 **읽기 전용** 쿼리만 사용.  
  예: `SELECT COUNT(*) FROM autoda.users;` 등으로 데이터 변경 없음 확인 가능.
- **결과**: (서버 실행 후) V1 DB/소스 변경 없음 확인함. (예/해당 없음)

---

## 7. 생성·수정 파일 목록

| 경로 | 설명 |
|------|------|
| docs/scripts/R0-TASK-002-FIX-2-runbook.sh | STEP 2~4 서버 일괄 실행 런북 (DBPW는 환경변수로만 전달) |
| docs/reports/R0-TASK-002-FIX-2-report.md | 본 보고서 |

서버에서 STEP 2 실행 시 추가 생성되는 파일 (기존과 동일):

- docs/v1-tables-overview.tsv  
- docs/v1-schema-full.sql  
- docs/v1-columns-detail.tsv  
- docs/v1-indexes.tsv  
- docs/v1-foreign-keys.tsv  

---

*본 보고서는 지시서 NT-V2-R0-TASK-002-FIX-2에 따라 작성되었습니다. STEP 1은 표님 수행, STEP 2~4는 서버에서 런북 또는 수동 실행 후 위 표를 채워 완료 보고하면 됩니다.*
