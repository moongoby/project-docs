# ShortFlow + StyleFlow 시스템 아키텍처 v1.0

> **최종 수정:** 2026-02-23
> **버전:** v1.0

---

## 1. 인프라 구성도

```
[NAS Synology]                    [서버 rfree-0009 (114.207.244.86)]
192.168.30.23 ──SSH:2222──────▶  /data/shortflow (심볼릭 → goodscode 11TB)
  │                               /data/styleflow (심볼릭 → goodscode 11TB)
  │  sync_nas.sh (30분)           │
  └──────────────────────────────▶│
                                  ├── Docker Compose
                                  │   ├── worker (pipeline_worker.py)
                                  │   ├── n8n (스케줄러 09/13/18h)
                                  │   ├── api (FastAPI :8000)
                                  │   ├── dashboard (Next.js :3000)
                                  │   └── redis (Phase 3)
                                  │
                                  ├── MySQL autoda (localhost)
                                  │   └── goods 77,109건
                                  │
                                  └── Supabase (PostgreSQL, 외부)
                                      ├── tenants, products, jobs, analytics
                                      └── sf_tenants, sf_brands, sf_videos
```

## 2. ShortFlow 파이프라인 (B2C)

```
[n8n 스케줄 09/13/18h]
  │
  ▼
Product Pick (Supabase) → AI Script (LLM + 7 아키타입)
  → AI Image → TTS (3-Stage) → FFmpeg Combine
  → 10-Layer 양산형 회피 엔진 (Originality Score)
  → Cross-Video Check → YouTube Upload (API v3)
  → Analytics Fetch (1h 간격)
```

## 3. StyleFlow 파이프라인 (B2B)

```
[NAS 촬영 원본 업로드]
  │
  ▼
Ingestion (sync/watcher) → Quality Grading (A/B/C)
  → Product Matching (autoda DB) → Template Selection (5종)
  → Video Editing (MOV→MP4, 세로 변환, 텍스트/워터마크)
  → 10-Layer 양산형 회피 엔진
  → QA Review (자동승인 기본값)
  → Multi-Platform Upload (IG/YT/TT)
  → Analytics → Report
```

## 4. 10-Layer 양산형 회피 엔진

```
Input → Layer 1 (Visual 3,125 조합)
      → Layer 2 (Script 7 아키타입)
      → Layer 3 (Voice rate/pitch/pause)
      → Layer 4 (BGM 30곡 로테이션)
      → Layer 5 (Metadata 10 공식)
      → Layer 6 (Upload ±30분 오프셋)
      → Layer 7 (Originality Score 0-100)
      → Layer 8 (Narrative 의견 삽입)
      → Layer 9 (Structural 4 구조)
      → Layer 10 (Cross-Video pHash+Chromaprint+TF-IDF)
      → Score ≥70: Upload / 50-69: Warning / <50: Regenerate
```

## 5. 공유 모듈 매핑

| 모듈 | ShortFlow | StyleFlow |
|------|-----------|-----------|
| 10-Layer 엔진 | ✅ | ✅ |
| FFmpeg | ✅ | ✅ |
| YouTube 업로더 | ✅ | ✅ |
| Supabase Auth/DB | ✅ | ✅ |
| 대시보드 프레임워크 | ✅ | ✅ |
| NAS 동기화 | ❌ | ✅ |
| 상품 매칭 (autoda) | ❌ | ✅ |
| 품질 등급 분류 | ❌ | ✅ |
| AI 스크립트 생성 | ✅ | ❌ |
| AI 이미지 생성 | ✅ | ❌ |
| 상품 추천 AI | ✅ | ❌ |

## 6. 디스크 구조

```
/dev/sda (루트 875GB, 76%)
  └── / (시스템, OS, 앱)

/dev/sdb1 (goodscode 11TB, 46%)
  └── /home/danharoo/www/data/files/goods/goodscode/
      ├── shortflow/  ← /data/shortflow 심볼릭 링크 대상
      └── styleflow/  ← /data/styleflow 심볼릭 링크 대상
```

## 7. 변경 이력

| 날짜 | 버전 | 변경 |
|------|------|------|
| 2026-02-23 | v1.0 | 최초 작성 |
