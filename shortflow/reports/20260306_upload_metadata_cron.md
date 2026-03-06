# SF-T011: 업로드 메타데이터 최적화 + 크론 피크타임 조정

**작업일**: 2026-03-06
**태스크**: SF-T011
**서버**: 114 (shortflow)
**우선순위**: P1-HIGH

---

## 1. 백업

```
/data/shortflow/backups/shortflow_pre_T011_20260306_160055.tar.gz (1차)
/data/shortflow/backups/shortflow_pre_T011_20260306_160730.tar.gz (BRIDGE 재실행)
/data/shortflow/backups/crontab_pre_T011.bak
```

---

## 2. 채널별 메타데이터 프리셋 (BRIDGE 갱신)

파일: `config/upload_metadata.json`

```json
{
  "economy": {
    "hashtags": ["#경제", "#재테크", "#주식", "#환율", "#돈", "#투자", "#3분경제", "#shorts"],
    "description_template": "{title}\n\n{hook}\n\n💰 매일 3분, 경제 상식이 쌓입니다\n\n{cta}\n\n{hashtags_str}\n\n⚠️ 본 영상은 정보 제공 목적이며 투자 조언이 아닙니다.",
    "tags": ["경제", "재테크", "주식", "환율", "투자", "돈관리", "3분경제", "shorts", "쇼츠"]
  },
  "health": {
    "hashtags": ["#건강", "#다이어트", "#음식", "#영양", "#건강정보", "#건강한입", "#shorts"],
    "description_template": "{title}\n\n{hook}\n\n🥗 매일 건강한 한 입!\n\n{cta}\n\n{hashtags_str}\n\n⚠️ 의학적 조언이 아닌 일반 건강 정보입니다.",
    "tags": ["건강", "다이어트", "음식", "영양소", "건강정보", "건강한입", "shorts", "쇼츠"]
  },
  "history": {
    "hashtags": ["#역사", "#한국사", "#세계사", "#역사이야기", "#역사5분", "#shorts"],
    "description_template": "{title}\n\n{hook}\n\n📚 5분이면 역사 한 편!\n\n{cta}\n\n{hashtags_str}",
    "tags": ["역사", "한국사", "세계사", "역사이야기", "역사5분", "shorts", "쇼츠"]
  }
}
```

변경 핵심:
- `{summary}` → `{hook}` (SF-T009 대본 hook 직접 사용)
- `{hashtags}` → `{hashtags_str}` (명확한 변수명)
- 면책 문구 템플릿 하단 포함 (economy, health)

---

## 3. 업로드 코드 수정 (scripts/run_v4_pipeline.py)

### 변경 사항

- `_build_description(channel, title, hook, cta, summary)` — 신규 변수(`hook`, `hashtags_str`) 지원, 구 변수(`summary`, `hashtags`) 하위 호환 유지
- `upload_with_privacy()`:
  - `title_options[0]` 우선 사용 (없으면 `title`, 없으면 `raw_title` 폴백)
  - `script_data.get("hook")` 로 hook 추출 (없으면 `summary` 폴백)
  - `description = _build_description(channel, script_title, hook=hook, cta=cta)`

---

## 4. 크론 시간 변경

### 최종 crontab

```
# ShortFlow v4 업로드 크론 (SF-T011: 한국 피크타임)
# economy: 07:30 / 12:00 / 19:00
30 7 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
0 12 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
0 19 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
# health: 07:40 / 12:10 / 19:10
40 7 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health >> /data/shortflow/logs/upload_health.log 2>&1
10 12 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health >> /data/shortflow/logs/upload_health.log 2>&1
10 19 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health >> /data/shortflow/logs/upload_health.log 2>&1
# alert: 07:55 / 12:25 / 19:25 (SF-T011: 업로드 25분 후)
55 7 * * * cd /data/shortflow && venv/bin/python scripts/send_alert_email.py >> /data/shortflow/logs/alert.log 2>&1
25 12 * * * cd /data/shortflow && venv/bin/python scripts/send_alert_email.py >> /data/shortflow/logs/alert.log 2>&1
25 19 * * * cd /data/shortflow && venv/bin/python scripts/send_alert_email.py >> /data/shortflow/logs/alert.log 2>&1
# daily: 23:30 (SF-T011: 유지)
30 23 * * * cd /data/shortflow && bash scripts/daily_report.sh >> /data/shortflow/logs/daily_report.log 2>&1
```

### 변경 근거

| 채널 | 이전 | 이후 | 이유 |
|------|------|------|------|
| economy | 09:00/13:00/18:00 | 07:30/12:00/19:00 | KR Shorts 피크 (출근전/점심/저녁) |
| health | 09:10/13:10/18:10 | 07:40/12:10/19:10 | economy 10분 후 |
| alert | (미설정) | 07:55/12:25/19:25 | 업로드 25분 후 알림 |
| daily | (미설정) | 23:30 | 일일 리포트 |

---

## 5. 테스트 결과

```
테스트 제목

이것 모르면 큰일납니다

💰 매일 3분, 경제 상식이 쌓입니다

구독하고 매일 경제 꿀팁!

#경제 #재테크 #주식 #환율 #돈 #투자 #3분경제 #shorts

⚠️ 본 영상은 정보 제공 목적이며 투자 조언이 아닙니다.
---
Tags: ['경제', '재테크', '주식', '환율', '투자', '돈관리', '3분경제', 'shorts', '쇼츠']
```

테스트 결과: **정상**

---

## 6. 완료 기준 체크

- [x] `config/upload_metadata.json` 생성 (hook/hashtags_str 변수 적용)
- [x] 업로드 코드에 `hook`, `hashtags_str`, `title_options[0]` 적용
- [x] 크론 시간 변경 (economy 07:30/12:00/19:00, health 07:40/12:10/19:10)
- [x] alert 크론 추가 (07:55/12:25/19:25)
- [x] daily 크론 추가 (23:30)
- [x] crontab 백업 (`backups/crontab_pre_T011.bak`)
- [x] 테스트 출력 정상
- [x] `.env`, `youtube_token_*.json` 수정 없음
- [x] 커밋 완료
