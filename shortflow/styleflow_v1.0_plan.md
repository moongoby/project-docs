# StyleFlow v1.0 – 쇼핑몰 영상 자동화 B2B SaaS 기획서

> **작성일**: 2026-02-22
> **버전**: v1.0
> **작성자**: ShortFlow 프로젝트팀
> **문서 경로**: /data/shortflow/docs/styleflow_v1.0_plan.md
> **상태**: 기획 완료 → 기술·개발 착수 대기

---

## 1. 프로젝트 개요

### 1.1 서비스 정의

StyleFlow는 온라인 쇼핑몰의 촬영 원본 영상(MOV/MP4)을 자동으로 분석·편집하여
Instagram Reels, YouTube Shorts, TikTok용 세로형 릴스를 생성하고, 복수 SNS 채널에
자동 업로드하는 B2B SaaS 플랫폼이다.

핵심 가치 명제: **"촬영만 하세요, 릴스는 저희가."**

1차 타겟은 뉴톡의 기존 유통 네트워크(수백 개 거래처)이며, 이들은 촬영 인프라를
보유하고 있으나 숏폼 영상 제작·관리 역량이 부족하다. 기존 대안(편집 인력 월 250-300만원,
대행사 월 100-300만원)의 1/8-1/9 비용으로 동등 이상의 결과물을 제공한다.

### 1.2 1차 타겟 브랜드

| 브랜드 | 역할 | 상태 |
|--------|------|------|
| 시크블랙 (chicblack) | 내부 파일럿, 기능 검증용 | Phase 1 진행 중 |
| 린다샵 (lindashop) | 2차 확장 대상 | Phase 2 |
| 뉴톡 거래처 5-10곳 | 외부 파일럿 | Phase 2 |

### 1.3 벤치마크

- **Reetkeem**: 32,500 팔로워, 5-15초 빠른 컷, 아웃핏 체크 스타일
- **SeoulBased**: 감성적 톤, 30-60초, GRWM 스타일

---

## 2. 수익 모델

### 2.1 요금제

| 요금제 | 월가격 | 영상/월 | 브랜드 수 | SNS 채널 | 핵심 기능 |
|--------|--------|---------|-----------|----------|-----------|
| Trial | 0원 (14일) | 20 | 1 | 1 | 기본 5 템플릿, 워터마크 포함 |
| Starter | 149,000원 | 100 | 1 | 2 | 워터마크 제거, 자동 업로드 |
| Growth | 349,000원 | 300 | 3 | 6 | 커스텀 템플릿, 10-Layer 회피, 주간 리포트 |
| Enterprise | 690,000원 | 1,000 | 10 | 30 | 화이트라벨, API, 전담 매니저 |
| Custom | 협의 | 무제한 | 무제한 | 무제한 | 온프레미스 옵션 |

가격 근거: 편집 인력 월급 250-300만원의 1/8-1/9 수준 (Starter 기준).
Growth 349,000원은 영상 편집 인력 1명 대비 월 300개 영상 자동 생산으로
압도적 비용 효율.

### 2.2 수익 시뮬레이션

| 시점 | Trial | Starter | Growth | Enterprise | 월 매출 |
|------|-------|---------|--------|------------|---------|
| 1개월 | 5 | 2 | 0 | 0 | 298,000원 |
| 3개월 | 10 | 8 | 2 | 0 | 1,890,000원 |
| 6개월 | 20 | 20 | 8 | 1 | 6,470,000원 |
| 12개월 | 30 | 30 | 20 | 5 | 17,450,000원 |

12개월 목표: Starter 30, Growth 20, Enterprise 5 = 월 17,450,000원.
ShortFlow v3.0과 합산: 월 약 24,520,000원.

---

## 3. 시스템 아키텍처

### 3.1 서버 환경

ShortFlow v3.0과 동일 서버(rfree-0009, 114.207.244.86) 공유.
프로젝트 경로: /data/shortflow (StyleFlow 전용 모듈 포함).
데이터 경로: /data/styleflow (촬영 원본 RAW, 생성 결과물 output).

### 3.2 공유 인프라 (ShortFlow v3.0과 공유)

| 모듈 | 역할 |
|------|------|
| FFmpeg 엔진 | 영상 변환·합성·자막·BGM 믹싱 |
| 10-Layer 양산형 회피 엔진 | 양산형 판정 회피 |
| YouTube/TikTok/Instagram 업로더 | 멀티플랫폼 업로드 |
| Supabase Auth + DB + RLS | 인증·데이터·멀티테넌트 격리 |
| 대시보드 프레임워크 | Next.js + Tailwind |
| Docker Compose | 컨테이너 오케스트레이션 |

### 3.3 StyleFlow 전용 모듈

| 파일 | 역할 |
|------|------|
| engine/ingestion.py | NAS/클라우드 원본 수집, 폴더 감시 |
| engine/product_matcher.py | DB(autoda) goods 테이블과 상품 자동 매칭 |
| engine/quality_grader.py | 촬영 원본 품질 자동 등급 분류 (A/B/C) |
| engine/editor.py | ReelEditor – MOV→MP4, 회전, 텍스트 오버레이, 워터마크 |
| api/routers/review.py | 검수(QA) API – 승인/반려/재생성 |
| api/routers/brands.py | 브랜드 관리 API – 로고, 폰트, 컬러, 해시태그 |
| api/routers/report.py | 성과 리포트 생성 API |
| api/routers/quality.py | 품질 등급 조회 API |

### 3.4 NAS 연동

| 항목 | 값 |
|------|-----|
| NAS | Synology DSM 7.2.1 |
| 내부 IP | 192.168.30.23 |
| 외부 IP | 183.96.69.193 |
| SSH 포트 | 2222 (라우터 포트포워딩) |
| 사용자 | newtalk |
| SSH 키 | /root/.ssh/id_nas |
| 동기화 스크립트 | /data/shortflow/engine/sync_nas.sh |
| 동기화 주기 | 30분 (crontab 등록 대기) |
| 전송 방식 | tar + SSH |

### 3.5 데이터베이스

#### Supabase (멀티테넌트 SaaS)

**sf_tenants** 테이블 (StyleFlow 전용):
```sql
CREATE TABLE sf_tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  contact_email TEXT UNIQUE NOT NULL,
  contact_phone TEXT,
  plan TEXT DEFAULT 'trial'
    CHECK (plan IN ('trial','starter','growth','enterprise','custom')),
  plan_expires_at TIMESTAMPTZ,
  nas_config JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**sf_brands** 테이블:
```sql
CREATE TABLE sf_brands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES sf_tenants(id),
  brand_name TEXT NOT NULL,
  logo_url TEXT,
  font_family TEXT DEFAULT 'NanumGothicBold',
  color_palette JSONB DEFAULT '{"primary":"#000000","secondary":"#FFFFFF"}',
  watermark_position TEXT DEFAULT 'bottom_right',
  default_hashtags TEXT[],
  shooting_guide JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**sf_channels** 테이블:
```sql
CREATE TABLE sf_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES sf_tenants(id),
  brand_id UUID REFERENCES sf_brands(id),
  platform TEXT CHECK (platform IN ('instagram','youtube','tiktok')),
  account_name TEXT,
  oauth_token JSONB,
  is_business_account BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**sf_videos** 테이블:
```sql
CREATE TABLE sf_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES sf_tenants(id),
  brand_id UUID REFERENCES sf_brands(id),
  source_file TEXT NOT NULL,
  source_quality_grade TEXT CHECK (source_quality_grade IN ('A','B','C')),
  template_type TEXT,
  product_name TEXT,
  product_price INTEGER,
  product_color TEXT,
  product_size TEXT,
  output_file TEXT,
  originality_score INTEGER,
  review_status TEXT DEFAULT 'auto_approved'
    CHECK (review_status IN ('pending','auto_approved','manual_approved','rejected','re_generate')),
  upload_status TEXT DEFAULT 'pending'
    CHECK (upload_status IN ('pending','scheduled','uploading','completed','failed')),
  scheduled_at TIMESTAMPTZ,
  uploaded_at TIMESTAMPTZ,
  upload_urls JSONB DEFAULT '{}',
  analytics JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**sf_upload_schedule** 테이블:
```sql
CREATE TABLE sf_upload_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES sf_tenants(id),
  brand_id UUID REFERENCES sf_brands(id),
  channel_id UUID REFERENCES sf_channels(id),
  day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6),
  time_slot TIME NOT NULL,
  template_preference TEXT,
  is_active BOOLEAN DEFAULT true
);
```

RLS는 모든 테이블에 tenant_id 기반으로 적용.

#### 기존 MySQL (autoda) – 상품 매칭용

goods 테이블 (77,109건)에서 상품명, 가격, 색상, 사이즈 등을 조회하여
영상 텍스트 오버레이에 자동 반영. cody_msg, cody_product_msg 테이블로
코디 정보와 상품 매핑.

### 3.6 파이프라인 흐름

```
[NAS/클라우드 업로드]
       │
       ▼
[1] Ingestion (engine/ingestion.py)
       │  sync_nas.sh (30분 간격) 또는 watcher.py (실시간)
       │  새 MOV/MP4 파일 감지
       ▼
[2] Quality Grading (engine/quality_grader.py) ★신규
       │  FFprobe → 해상도, 비트레이트, 노이즈, 밝기 분석
       │  Grade A: 정상 진행
       │  Grade B: 자동 업스케일/색보정 후 진행
       │  Grade C: 담당자 알림 → 수동 확인
       ▼
[3] Product Matching (engine/product_matcher.py)
       │  파일명/폴더명에서 코디 코드 추출
       │  → autoda.cody_product_msg → autoda.goods 조인
       │  → 상품명, 가격, 색상, 사이즈 자동 매칭
       ▼
[4] Template Selection
       │  5개 기본 템플릿:
       │    A. Outfit Check (빠른 컷)
       │    B. 가격쇼크 (가격 강조)
       │    C. GRWM (착장 과정)
       │    D. vs 코디 (비교)
       │    E. 신상모음 (컬렉션)
       │  브랜드 설정에 따라 커스텀 템플릿 추가 가능
       ▼
[5] Video Editing (engine/editor.py)
       │  MOV → MP4 변환 (H.264 High)
       │  가로(1920×1080) → 세로(1080×1920) 회전
       │  텍스트 오버레이 (상품명, 가격 – NanumGothicBold)
       │  브랜드 워터마크/로고 삽입
       │  BGM 믹싱
       │  인트로/아웃트로 자동 추가
       ▼
[6] 10-Layer 양산형 회피 엔진 (engine/anti_inauthentic.py)
       │  Originality Score 산출
       │  70+ → 통과, 50-69 → 수동 확인, <50 → 재생성
       ▼
[7] QA Review
       │  자동 승인 모드 (기본값):
       │    점수 70+ → 즉시 업로드 대기열
       │    점수 <70 → Slack/카카오톡 알림 → 수동 확인
       │  수동 승인 모드 (선택):
       │    모든 영상 → 대시보드 "검수 대기" 탭
       │    24시간 미확인 시 자동 리마인드
       ▼
[8] Multi-Platform Upload
       │  Instagram Reels (Graph API)
       │  YouTube Shorts (Data API v3)
       │  TikTok (Content Posting API)
       │  플랫폼별 메타데이터 자동 변환
       ▼
[9] Analytics Collection
       │  각 플랫폼 API로 조회수/좋아요/댓글/저장 수집
       │  sf_videos.analytics JSONB 업데이트
       ▼
[10] Report Generation
       │  주간 PDF 자동 발송 (선택)
       │  대시보드 실시간 표시
```

---

## 4. 촬영 원본 품질 자동 등급 분류

### 4.1 등급 기준 (engine/quality_grader.py)

| 등급 | 해상도 | 비트레이트 | 밝기 (Y) | 노이즈 | 처리 |
|------|--------|------------|----------|--------|------|
| A | ≥1080p | ≥8 Mbps | 50-200 | 낮음 | 정상 파이프라인 |
| B | 720-1080p | 4-8 Mbps | 30-50 or 200-230 | 중간 | 자동 보정 후 진행 |
| C | <720p | <4 Mbps | <30 or >230 | 높음 | 담당자 알림 |

### 4.2 자동 보정 (Grade B)

- 해상도 부족: Lanczos 업스케일 to 1080p
- 밝기 부족/과다: FFmpeg eq 필터 (brightness, contrast, gamma)
- 색온도 편차: FFmpeg colorbalance 필터

### 4.3 촬영 가이드 자동 생성

최초 온보딩 시 샘플 5개를 업로드하면, 평균 등급을 산정하고
개선이 필요한 항목별로 촬영 가이드를 자동 생성하여 제공한다:

- 조명: "정면 45도 2등 조명 권장, 최소 500룩스"
- 카메라: "1080p 이상, 29.97fps, 셔터스피드 1/60"
- 배경: "단색 또는 깔끔한 배경 권장"
- 구도: "세로 촬영 또는 가로 촬영 시 상하 여백 확보"

---

## 5. 검수(QA) 흐름

### 5.1 자동 승인 모드 (기본값)

목적: 쇼핑몰 담당자의 작업량 최소화.

- 양산형 회피 엔진 Originality Score 70점 이상 → 자동 승인 → 업로드 대기열
- 70점 미만 → Slack/카카오톡 알림 발송 → 대시보드에서 수동 확인
- 상품 매칭 실패 (가격·상품명 불일치) → 자동 플래그 → 수동 확인

### 5.2 수동 승인 모드 (선택)

- 모든 영상이 "검수 대기" 상태로 대시보드에 표시
- 썸네일 미리보기 + 15초 프리뷰 영상 제공
- 원클릭 승인/반려/재생성
- 24시간 미확인 시 자동 리마인드 (Slack/카카오톡/이메일)

### 5.3 예외 알림 체계

| 이벤트 | 알림 채널 | 내용 |
|--------|-----------|------|
| 품질 등급 C | Slack + 카카오톡 | "원본 품질 부족 – 수동 확인 필요" |
| Originality Score <70 | Slack | "양산형 점수 미달 – 검수 필요" |
| 상품 매칭 실패 | Slack | "DB 매칭 실패 – 수동 입력 필요" |
| 업로드 실패 | Slack + 이메일 | "API 오류 – 재시도 또는 점검 필요" |
| 24시간 미검수 | 카카오톡 | "미확인 영상 N건 – 확인 바랍니다" |

---

## 6. 5개 기본 템플릿

### Template A: Outfit Check

| 항목 | 값 |
|------|-----|
| 길이 | 7-15초 |
| 구성 | 빠른 컷 전환, 전신→상의→하의→악세서리 |
| 텍스트 | 상품명 + 가격 |
| BGM | 빠른 비트 (120+ BPM) |
| 벤치마크 | Reetkeem 스타일 |

### Template B: 가격쇼크

| 항목 | 값 |
|------|-----|
| 길이 | 10-20초 |
| 구성 | 가격 대형 텍스트 → 상품 클로즈업 → 전신 |
| 텍스트 | 가격 강조 + ₩ 표기 |
| BGM | 서스펜스 → 밝은 전환 |
| 효과 | 가격 등장 시 줌인 + 사운드 이펙트 |

### Template C: GRWM (Get Ready With Me)

| 항목 | 값 |
|------|-----|
| 길이 | 15-30초 |
| 구성 | 착장 과정 순서대로 (이너→아우터→신발→가방) |
| 텍스트 | 각 아이템별 상품명 |
| BGM | 감성적 톤 (90-110 BPM) |
| 벤치마크 | SeoulBased 스타일 |

### Template D: vs 코디

| 항목 | 값 |
|------|-----|
| 길이 | 15-25초 |
| 구성 | 좌우 분할 비교 (코디 A vs 코디 B) |
| 텍스트 | 각 코디 가격 합계 + 투표 유도 |
| BGM | 경쾌한 비교 느낌 |
| 인터랙션 | "댓글로 1 or 2 투표!" CTA |

### Template E: 신상모음

| 항목 | 값 |
|------|-----|
| 길이 | 20-30초 |
| 구성 | 3-5개 신상품 연속 전환 |
| 텍스트 | "이번주 신상" + 각 상품명/가격 |
| BGM | 업비트 컬렉션 느낌 |
| 효과 | 슬라이드 전환 + 넘버링 (1/5, 2/5, ...) |

---

## 7. 대시보드 설계

### 7.1 Screen 1 – Inbox (영상 모아보기)

- 기간 필터: 오늘 / 이번주 / 이번달
- 상태 필터: 대기 / 승인 / 업로드완료 / 실패
- 카드 뷰: 썸네일 + 상품명 + 브랜드 + 템플릿 + 상태 배지
- 원클릭 승인/반려 버튼
- 일괄 선택 + 일괄 승인

### 7.2 Screen 2 – Brand Management

- 브랜드 리스트 (카드 뷰)
- 브랜드 추가/수정 모달:
  - 로고 PNG 업로드
  - 폰트 선택 (시스템 폰트 또는 커스텀)
  - 컬러 팔레트 (primary, secondary, accent)
  - 워터마크 위치 (9-grid 선택)
  - 기본 해시태그 입력
  - 촬영 가이드 자동 생성 결과 표시

### 7.3 Screen 3 – Upload Schedule

- 주간 캘린더 뷰 (월-일, 시간대별)
- 플랫폼별 아이콘 (IG/YT/TT) 컬러 구분
- 드래그앤드롭으로 시간대 조정
- 슬롯별 영상 미리보기 썸네일
- 잔여 영상 수 / 이번주 목표 대비 진행률

### 7.4 Screen 4 – Performance Report

- 기간 선택 (7일/30일/90일)
- 브랜드별/상품별/템플릿별 필터
- 통합 지표: 총 조회수, 총 좋아요, 총 댓글, 총 저장, 평균 시청 시간
- 플랫폼별 분리 차트 (Instagram vs YouTube vs TikTok)
- TOP 10 성과 릴스 하이라이트
- 주간 PDF 자동 발송 토글 (이메일 지정)

### 7.5 Screen 5 – System & Quality

- 품질 등급 분포 파이 차트 (A/B/C 비율)
- 최근 등급별 원본 파일 목록
- NAS 연동 상태 (마지막 동기화 시간, 성공/실패)
- 10-Layer 엔진 적용 현황 (평균 Originality Score)
- 업로드 성공/실패 로그
- 디스크 사용량

---

## 8. 촬영 자산 규모 (시크블랙 기준)

| 항목 | 값 |
|------|-----|
| 모델 수 | 5명 |
| 주간 촬영 횟수 | 4-6회 |
| 촬영당 코디 수 | ~15벌 |
| 주간 MOV 수 | 60-90개 |
| 월간 MOV 수 | 300-450개 |
| MOV당 크기 | 10-18 MB |
| 월간 총 용량 | 약 5.5 GB |
| 현재 원본 | 11 MOV (20260220 촬영분, 147 MB) |
| 생성 릴스 | 40개 (5 템플릿 × 11 원본) |
| DB 상품 수 | 77,109건 |

---

## 9. 영상 스펙

| 항목 | 값 |
|------|-----|
| 원본 해상도 | 1920×1080 (가로) |
| 출력 해상도 | 1080×1920 (세로 9:16) |
| 회전 | -90° |
| 길이 | 7-30초 |
| 코덱 | H.264 High Profile |
| 오디오 | AAC 44.1 kHz |
| 프레임레이트 | 29.97 fps |
| 출력 크기 | 10-18 MB/영상 |

---

## 10. 파일 구조

```
/data/shortflow/
├── docs/
│   └── styleflow_v1.0_plan.md      ← 본 기획서
├── engine/
│   ├── ingestion.py                 # NAS 원본 수집 + 폴더 감시
│   ├── product_matcher.py           # DB 상품 자동 매칭
│   ├── quality_grader.py            # 품질 등급 분류 (A/B/C)
│   ├── editor.py                    # ReelEditor (MOV→릴스)
│   ├── sync_nas.sh                  # NAS 동기화 스크립트
│   ├── watcher.py                   # 파일 감시 watchdog
│   ├── anti_inauthentic.py          # 10-Layer 엔진 (ShortFlow 공유)
│   └── (나머지 10-Layer 모듈 – ShortFlow 공유)
├── api/routers/
│   ├── review.py                    # 검수 API
│   ├── brands.py                    # 브랜드 관리 API
│   ├── report.py                    # 성과 리포트 API
│   └── quality.py                   # 품질 등급 API
├── scripts/
│   ├── batch_reels_chicblack.py     # 시크블랙 일괄 생성 (Template A-C)
│   └── batch_reels_d_e.py           # Template D-E 일괄 생성
├── sql/
│   └── styleflow_schema.sql         # Supabase StyleFlow 테이블
└── (나머지 ShortFlow v3.0 공유 구조)

/data/styleflow/
├── raw/
│   └── chicblack/
│       └── 20260220/               # 날짜별 원본 MOV (11개, 147 MB)
├── output/
│   └── chicblack/                   # 생성된 릴스 MP4 + index.html
├── templates/
│   ├── template_a_outfit_check/
│   ├── template_b_price_shock/
│   ├── template_c_grwm/
│   ├── template_d_vs_codi/
│   └── template_e_new_arrival/
└── logs/
    └── styleflow_YYYYMMDD.log
```

---

## 11. 환경변수 (.env 추가분)

```bash
# === StyleFlow 전용 ===
STYLEFLOW_NAS_HOST=183.96.69.193
STYLEFLOW_NAS_PORT=2222
STYLEFLOW_NAS_USER=newtalk
STYLEFLOW_NAS_KEY=/root/.ssh/id_nas
STYLEFLOW_NAS_SYNC_INTERVAL=30
STYLEFLOW_RAW_PATH=/data/styleflow/raw
STYLEFLOW_OUTPUT_PATH=/data/styleflow/output
STYLEFLOW_QUALITY_GRADE_A_MIN_RESOLUTION=1080
STYLEFLOW_QUALITY_GRADE_B_MIN_RESOLUTION=720
STYLEFLOW_AUTO_APPROVE=true
STYLEFLOW_AUTO_APPROVE_THRESHOLD=70
STYLEFLOW_ALERT_SLACK_WEBHOOK=
STYLEFLOW_ALERT_KAKAO_KEY=

# === Instagram Graph API ===
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
INSTAGRAM_ACCESS_TOKEN=

# === TikTok Content Posting API ===
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_ACCESS_TOKEN=
```

---

## 12. BizProgress 코드 매핑

촬영 워크플로우에서 "릴스 생성 가능" 상태를 판별하기 위한
BizProgress 코드 정의 (실무자 미팅에서 확정 필요):

| BizProgress 코드 | 의미 | StyleFlow 동작 |
|-------------------|------|----------------|
| PHOTO_DONE | 사진 촬영 완료 | 대기 |
| VIDEO_DONE | 영상 촬영 완료 | 대기 |
| NAS_UPLOADED | NAS 업로드 완료 | sync 트리거 |
| REEL_READY | 릴스 생성 가능 | 파이프라인 시작 |
| REEL_GENERATED | 릴스 생성 완료 | 검수 대기 |
| REEL_APPROVED | 검수 완료 | 업로드 대기열 |
| REEL_UPLOADED | SNS 업로드 완료 | 완료 |

---

## 13. 리스크 관리

| 리스크 | 심각도 | 발생확률 | 대응 |
|--------|--------|----------|------|
| 영상 품질 편차 (외부 쇼핑몰) | 높음 | 높음 | 3단계 품질 등급 + 자동 보정 + 촬영 가이드 |
| 상품 매칭 오류 | 중간 | 중간 | 파일명 규칙 가이드 + 매칭 실패 시 수동 플래그 |
| Instagram API 제한 (비즈니스 계정 필수) | 중간 | 낮음 | 온보딩 시 비즈니스 계정 전환 가이드 제공 |
| B2B 영업 주기 길음 | 중간 | 높음 | Trial 14일 무료로 진입장벽 낮춤 + 뉴톡 네트워크 활용 |
| NAS 환경 다양성 (Synology 외 QNAP 등) | 낮음 | 중간 | 범용 SFTP/SSH 프로토콜 사용 + 클라우드 업로드 대안 |
| YouTube 양산형 정책 | 높음 | 중간 | 10-Layer 엔진 (ShortFlow 공유) |
| 담당자 검수 부담 | 중간 | 중간 | 자동 승인 기본값 + 예외 알림만 발송 |
| 서버 단일 장애점 | 높음 | 낮음 | Docker auto-restart + 일일 백업 + DR 계획 |

---

## 14. 사용자 확보 전략

### 14.1 Phase 1 – 내부 검증 (0-4주)

- 시크블랙 + 뉴톡 내부 2-3개 브랜드로 전체 파이프라인 검증
- 주간 성과 리포트 산출, 문제점 수집
- 촬영 가이드 문서 작성

### 14.2 Phase 2 – 파일럿 확산 (5-8주)

- 뉴톡 거래처 중 5-10곳 선정
- Trial 14일 무료 제공
- 전담 온보딩 지원 (NAS 설정, 폴더 명명 규칙, 비즈니스 계정 전환)
- 파일럿 종료 후 Starter/Growth 전환 유도
- 사례 데이터 수집 (조회수 증가율, 매출 변화)

### 14.3 Phase 3 – 공개 런칭 (9-12주)

- 랜딩 페이지 + 사례 영상 공개
- "촬영만 하세요, 릴스는 저희가" 메시지
- 채널별 마케팅:
  - 뉴톡 거래처 직접 영업 (전환율 최고)
  - 동대문 패션 커뮤니티 (네이버 카페·밴드)
  - 쇼핑몰 솔루션 파트너십 (카페24·고도몰·메이크샵 앱스토어 입점)
  - 인플루언서·스타일리스트 리퍼럴 (영상 5개 크레딧 제공)
  - SEO 블로그 ("쇼핑몰 릴스 자동화", "인스타그램 릴스 만들기")
- 결제 연동 (토스페이먼츠)
- 통신판매업 신고 완료

### 14.4 Phase 4 – 확대 (3-6개월)

- 동대문 도매 브랜드, 자사몰 운영자, 라이브커머스 업체 확대
- Growth/Enterprise 영업 본격화
- 화이트라벨(OEM) 옵션으로 대형 플랫폼·대행사 제공
- 패션 외 카테고리 확장 (뷰티, 인테리어, 식품)

### 14.5 리퍼럴 프로그램

기존 고객이 신규 고객을 소개하면 양측에 영상 5개 크레딧 제공.
성공적인 전환 시 다음 달 요금 10% 할인.

---

## 15. 락인(Lock-in) 전략

### 15.1 데이터 락인

브랜드 자산(로고, 폰트, 컬러, 해시태그, 검수 규칙), 성과 데이터(월별 리포트,
상위 템플릿, 최적 시간대), 상품 매칭 히스토리가 StyleFlow에 축적.
이관 시 모든 설정과 히스토리를 재구축해야 함.

### 15.2 워크플로우 락인

NAS 촬영 폴더 → StyleFlow 자동 감지 → 릴스 생성 → SNS 업로드까지
촬영 워크플로우 전체에 StyleFlow가 통합. 분리 시 프로세스 재설계 필요.

### 15.3 채널 락인

Instagram/YouTube/TikTok 비즈니스 계정 OAuth 연결 완료 상태에서
서비스 이전 시 재인증·재설정 부담.

### 15.4 학습 락인

담당자가 대시보드 사용법, 검수 프로세스, 촬영 가이드에 익숙해진 후
새 서비스 학습 비용이 스위칭 비용으로 작용.

### 15.5 네트워크 락인 (Phase 4)

브랜드 간 크로스 코디(교차 상품 노출) 기능 도입 시,
참여 브랜드가 많을수록 노출 효과 증가 → 네트워크 효과.

---

## 16. 다음 주 실무자 미팅 어젠다

| 주제 | 확인 사항 |
|------|-----------|
| 영상 디자인 | 브랜드 가이드(폰트, 사이즈, 컬러, 위치), 로고 PNG, 레퍼런스 릴스 3-5개, 텍스트 정보 범위 |
| BGM | 스타일 방향, 저작권 프리 소스/구독(Epidemic Sound), 촬영 원본 오디오 유지 여부 |
| 촬영 프로세스 | 폴더 명명 규칙, BizProgress 코드 확정, NAS 업데이트 버튼 기능 |
| 업로드 운영 | Instagram/TikTok/YouTube 계정 상태, 비즈니스 계정 전환, 일일 업로드 빈도·시간대, 캡션/해시태그 스타일 |

---

## 17. 액션 항목

| # | 작업 | 담당 | 상태 | 우선순위 |
|---|------|------|------|----------|
| 1 | 실무자 미팅 피드백 수렴 | 대표 | ⬜ | ★★★ |
| 2 | 품질 등급 분류 엔진 구현 | 개발 | ⬜ | ★★★ |
| 3 | 검수 QA API + 대시보드 구현 | 개발 | ⬜ | ★★★ |
| 4 | 브랜드 관리 대시보드 구현 | 개발 | ⬜ | ★★★ |
| 5 | crontab NAS 동기화 등록 | 개발 | ⬜ | ★★★ |
| 6 | DB 비밀번호 .env 설정 | 개발 | ⬜ | ★★★ |
| 7 | 시크블랙 로고 PNG 확보 | 대표 | ⬜ | ★★☆ |
| 8 | BizProgress 코드 확정 | 대표 | ⬜ | ★★☆ |
| 9 | Instagram Graph API 설정 | 개발 | ⬜ | ★★☆ |
| 10 | TikTok Content Posting API 설정 | 개발 | ⬜ | ★★☆ |
| 11 | YouTube 채널 확인 + OAuth | 대표 | ⬜ | ★★☆ |
| 12 | BGM 라이브러리 확보 | 개발 | ⬜ | ★★☆ |
| 13 | 파일럿 대상 거래처 5곳 선정 | 대표 | ⬜ | ★★☆ |
| 14 | 린다샵 파이프라인 복제 | 개발 | ⬜ | ★☆☆ |
| 15 | 카페24 앱스토어 입점 준비 | 개발 | ⬜ | ★☆☆ |
| 16 | 토스페이먼츠 결제 연동 | 개발 | ⬜ | ★☆☆ |

---

## 18. 핵심 URL

| 용도 | URL |
|------|-----|
| 릴스 미리보기 (데모) | http://114.207.244.86:8888/index.html |
| 대시보드 (구축 예정) | http://114.207.244.86:3000 |
| 뉴톡 관리자 | (내부 URL) |
| 뉴톡 쇼핑몰 | (시크블랙 등) |
| Instagram Graph API | https://developers.facebook.com/docs/instagram-api |
| TikTok Content Posting API | https://developers.tiktok.com/doc/content-posting-api |
| YouTube Data API v3 | https://developers.google.com/youtube/v3 |

---

> **문서 끝 – StyleFlow v1.0 기획서**
> 최종 수정: 2026-02-22
