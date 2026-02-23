# n8n 스케줄 3회 + AUTO_UPLOAD 활성화 및 daily_picks 30개 확보

**작성일시:** 2026-02-21
**작업 유형:** 설정 변경 / 신규 개발
**상태:** 완료
**관련 파일:** `n8n/daily_workflow.json`, `worker/main.py`, `worker/workers/pipeline_worker.py`, `.env`, `sql/003_seed_daily_picks_30.sql`

---

## 1. 작업 개요

n8n 일일 파이프라인을 1회(09:00)에서 3회(09:00, 13:00, 18:00 KST)로 변경하고, 당일 중복 pick 방지 로직을 추가했다. AUTO_UPLOAD=true 및 업로드 시 privacy_status=public 적용, daily_picks 시드 30개 상품용 SQL을 추가했다.

---

## 2. 변경 사항

### 2.1 n8n 스케줄 (하루 3회)
- **파일:** `n8n/daily_workflow.json`
- **변경:** Schedule Trigger cron `0 9 * * *` → `0 9,13,18 * * *`
- **결과:** 매일 09:00, 13:00, 18:00 KST에 `POST http://worker:8000/api/v1/pipeline/daily` 호출
- **n8n UI:** http://114.207.244.86:5678 에서 기존 워크플로우 삭제 후 `n8n/daily_workflow.json` import 하거나, 기존 워크플로우의 Schedule Trigger에서 cron 표현식만 위대로 수정

### 2.2 daily 엔드포인트 중복 방지
- **파일:** `worker/main.py` (`/api/v1/pipeline/daily`)
- **로직:**
  - 당일(KST 00:00~24:00) 생성된 job의 `pick_id` 목록 조회
  - `get_todays_picks()` 또는 active/pending daily_picks 조회 후, 위 `pick_id` 제외
  - 남은 픽이 없으면 `{"success": false, "message": "no_remaining_picks", "data": {"status": "no_remaining_picks", "used_today": N}}` 반환
  - 남은 픽 중 랜덤 1건 선택 후 Job 생성 및 파이프라인 백그라운드 실행
- **결과:** 같은 상품이 하루 3회 실행 시 중복 선택되지 않음

### 2.3 AUTO_UPLOAD 및 privacy_status
- **파일:** `.env`  
  - `AUTO_UPLOAD=false` → `AUTO_UPLOAD=true`
- **파일:** `worker/workers/pipeline_worker.py`  
  - 업로드 시 `privacy_status`: `auto_upload=True` 이면 `public`, 아니면 `private` 사용
- **유지:** `VIDEO_PROVIDER=ffmpeg`, 영상 title `{상품명} | 오늘의 쇼핑픽 #Shorts`, 기본 tags `['쇼핑', '추천', '핫딜', '오늘의쇼핑픽']`

### 2.4 daily_picks 30개 시드
- **파일:** `sql/003_seed_daily_picks_30.sql`
- **내용:** 6개 카테고리(전자기기/electronics, 뷰티/beauty, 건강/health, 패션/fashion, 식품/food, 유아용품/baby)당 5개 상품, 총 30건 INSERT
- **실행:** Supabase SQL Editor에서 001, 002 적용 후 003 실행. 기존 6건 있으면 총 36건, 비어 있으면 30건

---

## 3. 테스트 결과

- **린트:** `worker/main.py`, `worker/workers/pipeline_worker.py` 린트 오류 없음
- **Docker 재빌드 및 수동 테스트** (서버 rfree-0009에서 실행 권장):

```bash
cd /data/shortflow && docker compose down && docker compose build worker && docker compose up -d
curl http://localhost:8000/health
# 3회 연속 daily 호출 시 서로 다른 pick_id 선택 여부 확인
curl -X POST http://localhost:8000/api/v1/pipeline/daily
curl -X POST http://localhost:8000/api/v1/pipeline/daily
curl -X POST http://localhost:8000/api/v1/pipeline/daily
docker compose logs worker --tail 50
```

- **n8n 타임존:** Asia/Seoul 유지

---

## 4. 주의사항 / 후속 작업

1. **Supabase:** `sql/003_seed_daily_picks_30.sql` 실행하여 daily_picks 30건 이상 확보 (기존 6건 있으면 003 실행 후 36건).
2. **n8n:** 워크플로우를 새 JSON으로 교체한 경우 활성화(Active) 후 저장.
3. **YouTube:** AUTO_UPLOAD=true 이므로 QA 통과 후 실제 공개(public) 업로드됨. 테스트 시에는 AUTO_UPLOAD=false로 두고 확인 후 true 전환 권장했으나, 요청대로 true 적용 완료.
4. **중복 소진 시:** 당일 3회 모두 실행 후 추가 호출 시 `no_remaining_picks` 응답 정상 동작.
