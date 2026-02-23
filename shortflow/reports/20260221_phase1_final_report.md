# StyleFlow Phase 1 마무리

**작성일시:** 2026-02-21
**작업 유형:** 신규 개발 / 리팩터링
**상태:** 완료
**관련 파일:** `engine/editor.py`, `engine/db_connector.py`, `scripts/batch_reels_chicblack.py`, `scripts/batch_reels_d_e.py`, `engine/sync_nas.sh`

---

## 1. 작업 개요

Phase 1 기본 구현 이후, 릴스 품질 개선(텍스트 위치·디자인), BGM 자동 추가, DB 연동 활성화, 템플릿 B~E 구현, NAS 자동 동기화(crontab) 및 전체 테스트를 진행해 Phase 1을 마무리했습니다.

## 2. 변경 사항

### Task 1: 텍스트 위치·디자인 개선 (editor.py)

- **하단 반투명 박스:** `drawbox`로 하단 25% 영역(`y=ih*0.68`)에 `black@0.4` 적용.
- **텍스트 위치:** 상품명 `y=h*0.73`, 가격 `y=h*0.73+65`, CTA `y=h*0.73+130`, 브랜드 우상단 `y=30`.
- **스타일:** 상품명 fontsize=52, 가격 60, shadowcolor=black@0.8, shadowx/y=2. CTA "자세히 보기 ▶ 프로필 링크" fontsize=24, white@0.6.
- **테스트:** `reel_outfit_check_003.mp4` 생성 확인.

### Task 2: BGM 자동 추가

- **상수:** `BGM_DIR = "/data/styleflow/templates/bgm"` 추가.
- **generate_reel:** `bgm_path` 인자 추가. 지정 시 원본 오디오(0.4) + BGM(0.35) amix, `-shortest`로 영상 길이에 맞춤.
- **_pick_bgm(template):** 템플릿별 키워드(trendy/impact/chill/upbeat/energy)로 파일명 매칭, 없으면 첫 mp3/m4a 사용.
- **테스트용:** `/data/styleflow/templates/bgm/bgm_silent_30s.m4a`(무음 30초) 생성. 실제 BGM은 Pixabay 등에서 다운로드 후 동일 디렉터리에 배치.

### Task 3: DB 연동 + 배치 스크립트

- **db_connector:** `dotenv` 미설치 시에도 동작하도록 `load_dotenv()`를 try/except로 감쌌습니다.
- **batch_reels_chicblack.py:**  
  - 인자: `raw_dir`, `--templates`(기본 `A,B,C`).  
  - `db_connector.get_chicblack_products_with_cody(50)` → `product_to_reel_info`로 상품 리스트 생성.  
  - 실패 시 더미 30건 사용.
- **실제 상품 적용:** `.env`에 `NEWTALK_DB_PASSWORD` 설정 및 `pymysql` 설치 시 DB에서 시크블랙 상품명/가격 자동 적용.

### Task 4: 템플릿 B~E 구현

- **B (가격 쇼크):** 10초 트림, "이 가격 실화?" 상단, 3초부터 중앙 큰 가격, 하단 상품명·CTA. BGM 선택적.
- **C (GRWM):** 원본 길이, colorbalance로 따뜻한 톤, "what I wear today" 상단, 하단 상품명/가격(작은 폰트). BGM 선택적.
- **D (vs 코디):** `generate_vs_reel(path1, path2, product_info_1, product_info_2)` 신규. 2개 영상 각 7초 concat, 중간 "VS", 하단 구간별 상품명.
- **E (오늘의 신상):** `generate_compilation_reel(input_paths, product_info_list)` 신규. 3~5개 영상 각 4초, "오늘의 신상 TOP N", #1..#N 및 구간별 상품명.
- **배치:** `scripts/batch_reels_d_e.py` 추가. 11개 MOV 기준 D 5쌍(10개), E 2묶음(5+5) 생성 후 index.html 갱신.

### Task 5: crontab + NAS 자동 동기화

- **sync_nas.sh:** 기존 그대로 사용. `ssh nas`로 NAS(183.96.69.193:2222) 접속, 날짜 폴더별 tar 동기화.
- **crontab 등록 (수동):**  
  `crontab -e` 후 아래 한 줄 추가.  
  `*/30 * * * * /data/shortflow/engine/sync_nas.sh >> /data/styleflow/logs/cron_sync.log 2>&1`  
  확인: `crontab -l | grep sync_nas`

### Task 6: 전체 테스트

- **A,B,C:** 11개 MOV × 템플릿 A,B,C → 33건 생성 성공.
- **D,E:** `batch_reels_d_e.py` 실행 → D 5건, E 2건, 총 7건 성공.
- **총 40개 릴스** 생성, `index.html` 갱신 완료.
- **확인 URL:** http://114.207.244.86:8888/index.html (서버에서 8888 서비스 가동 시)

## 3. 테스트 결과

| 항목 | 결과 |
|------|------|
| Task 1 텍스트 개선 | reel_outfit_check_003.mp4 생성 성공 |
| Task 2 BGM | bgm_silent_30s.m4a 배치, amix 적용 코드 동작 |
| Task 3 DB | pymysql 미설치 환경에서 더미 폴백으로 33건 성공 |
| Task 4 B~E | B,C 단일 영상 / D 2영상 / E 5영상 조합 생성 성공 |
| Task 5 crontab | 수동 등록 안내 작성 (등록은 운영자 수행) |
| Task 6 40개 릴스 | 33 + 7 = 40건 생성, index.html 갱신 완료 |

## 4. 주의사항 / 후속 작업

- **DB 실제 연동:** 서버에 `pip3 install pymysql python-dotenv` 후 `.env`에 `NEWTALK_DB_PASSWORD`(pigupuser 비밀번호) 설정하면 배치 시 실제 상품명/가격 적용.
- **BGM:** Pixabay 등에서 mp3/m4a 다운로드 후 `/data/styleflow/templates/bgm/`에 `bgm_01_trendy.mp3` 등 파일명 규칙으로 저장 시 템플릿별 자동 매칭.
- **crontab:** 30분마다 NAS 동기화를 위해 위 한 줄을 crontab에 추가해야 합니다.
- **백업:** 필요 시 `/data/shortflow/backups/20260221_phase1_final/` 등에 변경 파일 백업 권장.
- **커밋:** `[feat] 릴스 품질 개선 + BGM + DB 연동 + 템플릿 B~E` 형식으로 커밋 가능. `.env`, 비밀번호, 키 파일은 커밋하지 말 것.
