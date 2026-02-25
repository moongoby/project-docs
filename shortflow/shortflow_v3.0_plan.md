# ShortFlow v3.0 – AI YouTube Shorts 자동화 SaaS 기획서

> **작성일**: 2026-02-22
> **버전**: v3.0
> **작성자**: ShortFlow 프로젝트팀
> **문서 경로**: /data/shortflow/docs/shortflow_v3.0_plan.md
> **상태**: 기획 완료 → 기술·개발 착수 대기

---

## 1. 프로젝트 개요

### 1.1 서비스 정의

ShortFlow는 쿠팡 파트너스 제휴 링크를 기반으로 YouTube Shorts 영상을 AI가 자동
생성·편집·업로드하는 B2C SaaS 플랫폼이다. 사용자는 쿠팡 상품 URL만 입력하면
스크립트 작성, 이미지 생성, TTS 음성 합성, FFmpeg 영상 합성, YouTube 업로드까지
전 과정이 자동으로 처리된다.

핵심 차별점은 YouTube의 'Inauthentic Content' 정책(2025-07-15 시행)에 대응하는
**10-Layer 양산형 회피 엔진**으로, 경쟁사 4곳(Reelbox, 패스트컷, 오토판다, 크몽 외주)
모두에 부재한 고유 기능이다.

### 1.2 운영 채널

- **채널명**: 템빨신상맨
- **채널 URL**: https://www.youtube.com/channel/UCqpf3lJQio6EBHxthLQob0g
- **플랫폼**: YouTube Shorts (Phase 1), TikTok·Instagram Reels (Phase 4)

### 1.3 수익 모델

#### 1차 수익 – 쿠팡 파트너스 수수료

쿠팡 파트너스 제휴 링크를 통한 판매 수수료 3-10%. 영상 설명란에 제휴 링크를 삽입하고,
시청자가 링크를 클릭하여 24시간 이내 구매 시 수수료가 발생한다.

#### 2차 수익 – YouTube AdSense

구독자 1,000명 + 최근 90일 Shorts 조회수 1,000만 회 달성 시 YouTube 파트너 프로그램
(YPP) 가입 가능. Shorts RPM은 약 14-84원/1,000회 수준이다.

#### 3차 수익 – SaaS 구독료

멀티테넌트 SaaS로 전환 후 월정액 구독 수익.

### 1.4 상품 전략

총 30개 상품으로 시작, 카테고리별 배분은 다음과 같다:

| 카테고리 | 상품 수 | 비중 | 평균 수수료율 | 비고 |
|----------|---------|------|---------------|------|
| 뷰티 | 8 | 27% | 5-7% | 전환율 최고 |
| 식품 | 7 | 23% | 3-5% | 검색량 최고 |
| 패션 | 5 | 17% | 3-5% | 시각적 임팩트 |
| 건강 | 4 | 13% | 5-8% | 고단가 |
| 생활가전 | 3 | 10% | 3-5% | 안정적 수요 |
| 육아 | 3 | 10% | 3-5% | 충성 고객층 |

주간 관리: 월요일 조회수/전환율 분석, 수요일 저성과 상품 교체 + 10개 추가,
금요일 A/B 테스트 분석, 일요일 다음주 DB 로드.

---

## 2. 시스템 아키텍처

### 2.1 서버 환경

| 항목 | 값 |
|------|-----|
| 서버명 | rfree-0009 |
| IP | 114.207.244.86 |
| OS | Linux |
| 프로젝트 경로 | /data/shortflow |
| 데이터 경로 | /data/styleflow |
| NAS | Synology DSM 7.2.1, 내부 192.168.30.23, 외부 183.96.69.193 |
| NAS SSH | 포트 2222, 사용자 newtalk, 키 /root/.ssh/id_nas |
| 라우터 | ipTIME A8004T-XR, 관리자 http://192.168.30.1 |

### 2.2 Docker Compose 구성

```yaml
services:
  worker:        # 파이프라인 워커 (pipeline_worker.py)
  n8n:           # 워크플로우 스케줄러
  api:           # FastAPI 백엔드
  dashboard:     # Next.js + Tailwind 프론트엔드
  redis:         # Phase 3에서 추가 (작업 큐)
```

### 2.3 데이터베이스

#### Supabase (PostgreSQL + Auth + RLS + Realtime)

**tenants** 테이블:
```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free','starter','pro','business')),
  plan_expires_at TIMESTAMPTZ,
  style_seed JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**channels** 테이블:
```sql
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  platform TEXT CHECK (platform IN ('youtube','tiktok','instagram')),
  channel_name TEXT,
  oauth_token JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**products (daily_picks 확장)** 테이블:
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  product_name TEXT NOT NULL,
  category TEXT,
  price INTEGER,
  coupang_url TEXT,
  affiliate_link TEXT,
  video_mode TEXT DEFAULT 'ai_generate'
    CHECK (video_mode IN ('ai_generate','edit_source')),
  video_source_url TEXT,
  status TEXT DEFAULT 'pending'
    CHECK (status IN ('pending','queued','processing','completed','failed','dead_letter')),
  picked_date DATE,
  originality_score INTEGER,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**jobs** 테이블:
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  product_id UUID REFERENCES products(id),
  channel_id UUID REFERENCES channels(id),
  template_type TEXT,
  script_archetype TEXT,
  structural_pattern TEXT,
  status TEXT DEFAULT 'queued',
  originality_score INTEGER,
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  video_url TEXT,
  youtube_video_id TEXT,
  uploaded_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**analytics** 테이블:
```sql
CREATE TABLE analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES jobs(id),
  tenant_id UUID REFERENCES tenants(id),
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  watch_time_pct NUMERIC(5,2),
  coupang_clicks INTEGER DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  fetched_at TIMESTAMPTZ DEFAULT now()
);
```

RLS(Row Level Security)는 모든 테이블에 tenant_id 기반으로 적용하여
사용자 간 데이터를 완전히 격리한다.

#### 기존 MySQL (autoda) – 뉴톡 상품 DB

| 항목 | 값 |
|------|-----|
| DB명 | autoda |
| 호스트 | localhost |
| 사용자 | pigupuser |
| 비밀번호 | .env (NEWTALK_DB_PASSWORD) |
| 주요 테이블 | goods (77,109건), cody_msg, cody_product_msg |

### 2.4 파이프라인 흐름

```
[n8n 스케줄러 09:00/13:00/18:00 KST]
         │
         ▼
[1] Product Pick ─── Supabase에서 status='pending' 상품 선택
         │            (요금제별 우선순위: Business > Pro > Starter > Free)
         ▼
[2] Script Generation ─── LLM (Claude/GPT) + 7 아키타입 중 선택
         │                   + Narrative Injection (상품별 고유 의견)
         ▼
[3] Image Generation ─── AI 이미지 생성 또는 상품 이미지 수집
         │
         ▼
[4] TTS ─── 3-Stage Fallback: ElevenLabs → Google Cloud TTS → Edge-TTS
         │    Voice Variation: rate 0.95-1.15, pitch -2~+2, pause 0.3-0.8s
         ▼
[5] FFmpeg Combine ─── 이미지 슬라이드쇼 + TTS 오디오 + BGM 믹싱
         │               + 자막 오버레이 + 브랜드 워터마크
         │               + Structural Variation (4가지 구조 패턴)
         ▼
[6] 10-Layer 양산형 회피 엔진 ─── Originality Score 산출
         │                          70+ → 통과
         │                          50-69 → 경고/수동 확인
         │                          <50 → 자동 재생성
         ▼
[7] Cross-Video Dissimilarity Check ─── 최근 20개 영상 대비 유사도 검사
         │                                pHash + Chromaprint + TF-IDF
         │                                임계값 0.85 초과 시 재생성
         ▼
[8] YouTube Upload ─── YouTube Data API v3 (Videos.insert)
         │              OAuth 2.0, Resumable Upload (10MB chunks)
         │              일일 6건 (10,000 units, 1,600/upload)
         ▼
[9] Status Update ─── Supabase products.status = 'completed'
         │              jobs 테이블에 youtube_video_id 기록
         ▼
[10] Analytics Fetch ─── 1시간 간격으로 YouTube API videos.list 호출
                          views, likes, comments 수집 → analytics 테이블
```

### 2.5 2-Track 아키텍처

**Track A (ai_generate)**: 상품 URL → AI 스크립트 → AI 이미지 → TTS → FFmpeg
→ 업로드. 완전 자동.

**Track B (edit_source)**: 실제 촬영 원본 MOV/MP4 → 자동 편집(인트로/아웃트로,
텍스트 오버레이, BGM) → 업로드. StyleFlow 파이프라인과 공유.

---

## 3. 10-Layer 양산형 회피 엔진

### 3.1 배경

YouTube는 2025-07-15 'Inauthentic Content' 정책을 시행하여, "mass-produced or
repetitive content … content that looks like it's made with a template with little
to no variation across videos"를 수익화에서 제외한다. 2026-01 기준 AI 생성 채널
상위 100개 중 16개가 삭제되었으며, 이 추세는 가속화되고 있다.

YouTube가 허용하는 사례: "Similar content, where each video talks specifically
about the qualities of the subject you're featuring." 즉 상품별 고유 리뷰 톤을
유지하면 동일 채널 내 유사 포맷 자체는 허용된다.

### 3.2 감지 신호 분석

YouTube가 감지하는 것으로 판단되는 6가지 신호:

1. **시각적 동일성** – 레이아웃, 색상, 전환, 텍스트 위치의 반복
2. **오디오 패턴** – 동일 TTS 보이스, 동일 말투, 동일 BGM
3. **스크립트 구조** – 고정 문구, 동일한 인트로/아웃트로 대사
4. **메타데이터 유사성** – 제목/설명/태그 거의 동일
5. **시청자 행동** – 평균 시청 2-3초, 좋아요·댓글 0
6. **업로드 패턴** – 하루 5건 이상, 정확히 동일 간격

### 3.3 10개 레이어 상세

#### Layer 1: Visual Variation (engine/visual_variation.py)

5개 시각 컴포넌트 × 5가지 변형 = 3,125 조합.

| 컴포넌트 | 변형 예시 |
|----------|-----------|
| 텍스트 위치 | 상단 중앙, 하단 좌측, 중앙, 우측 하단, 상단 좌측 |
| 배경 스타일 | 단색 그라디언트, 블러 이미지, 패턴, 다크 오버레이, 라이트 |
| 색상 테마 | 웜톤, 쿨톤, 네온, 파스텔, 모노크롬 |
| 전환 효과 | 페이드, 슬라이드, 줌인, 와이프, 디졸브 |
| 이미지 배치 | 풀스크린, 좌측 50%, 우측 50%, 상하 분할, 원형 마스크 |

최근 10개 영상에 사용된 조합은 자동 제외.

#### Layer 2: Script Variation (engine/script_variation.py)

7개 스크립트 아키타입:

1. **체험 리뷰형** – "직접 써봤는데…"
2. **비교 분석형** – "A vs B, 뭐가 나을까?"
3. **질문 유도형** – "이거 아직도 모르세요?"
4. **랭킹형** – "TOP 3 추천"
5. **문제 해결형** – "이 고민 해결해드립니다"
6. **트렌드 알림형** – "요즘 이게 대세!"
7. **반전 후크형** – "절대 사지 마세요… 라고 했다가"

각 아키타입별로 인트로 5개, 본문 전환 5개, 아웃트로 5개 문구를 사전 등록하고,
LLM이 상품 속성에 맞춰 변형 생성.

#### Layer 3: Voice Variation (engine/voice_variation.py)

| 파라미터 | 범위 | 적용 방식 |
|----------|------|-----------|
| 속도 (rate) | 0.95 - 1.15 | ±0.05 단위 무작위 |
| 피치 (pitch) | -2 ~ +2 st | ±1 단위 무작위 |
| 일시정지 (pause) | 0.3 - 0.8s | 문장 간 무작위 |
| 보이스 ID | 2-3개 로테이션 | Google Cloud + ElevenLabs |

TTS 엔진 3-Stage Fallback:
- 1순위: ElevenLabs (Pro/Business 요금제)
- 2순위: Google Cloud TTS (Starter 요금제, 보이스 ko-KR-Chirp3-HD-Kore)
- 3순위: Edge-TTS (Free 요금제, 비용 무료)

#### Layer 4: BGM Variation (engine/bgm_variation.py)

최소 30곡 라이브러리, 카테고리별 5곡 이상. 볼륨 0.2-0.4 범위 무작위,
시작 지점 무작위 오프셋 (0-30초), 최근 5곡 자동 제외.

#### Layer 5: Metadata Variation (engine/metadata_variation.py)

**제목 공식 10가지**:
1. `[상품명] ₩[가격] | [브랜드] #Shorts`
2. `[숫자]가지 이유로 [상품명] 추천 #Shorts`
3. `[감정트리거] [상품명] 리뷰 #Shorts`
4. `₩[가격]에 이 퀄리티? [상품명] #Shorts`
5. `[카테고리] 추천 TOP [숫자] #Shorts`
6. `[상품명] 솔직 후기 (feat. [특징]) #Shorts`
7. `이걸 [가격]에? [상품명] 언박싱 #Shorts`
8. `[시즌] 필수템 [상품명] #Shorts`
9. `[문제] 해결! [상품명] 추천 #Shorts`
10. `[상품명] vs [대안] 비교 리뷰 #Shorts`

제목 ≤100자, 설명 ≤5,000자, 태그 고정 5개 + 동적 10-15개, 순서·구성 매번 변경.

#### Layer 6: Upload Pattern (engine/upload_pattern.py)

기본 슬롯: 09:00, 13:00, 18:00 KST.
각 슬롯에 ±30분 무작위 오프셋 적용.
주말은 1-2건으로 감소, 월 1-2회 휴일(업로드 0건) 삽입.

#### Layer 7: Originality Scorer (engine/originality_scorer.py)

| 항목 | 점수 범위 | 측정 방법 |
|------|-----------|-----------|
| 시각 변주도 | 0-20 | 최근 10개 대비 레이아웃 해밍 거리 |
| 스크립트 독창성 | 0-20 | TF-IDF 코사인 유사도 역수 |
| TTS 변주도 | 0-20 | rate+pitch+pause 엔트로피 |
| BGM 변주도 | 0-20 | 곡 ID + 시작지점 + 볼륨 차이 |
| 메타데이터 변주도 | 0-20 | 제목/태그 자카드 거리 |
| **합계** | **0-100** | |

- 70점 이상: 자동 업로드
- 50-69점: 경고 로그 + 관리자 수동 확인
- 50점 미만: 자동 재생성 (최대 3회)

#### Layer 8: Narrative Injection (engine/narrative_injection.py) ★신규

YouTube가 명시적으로 허용하는 "each video talks specifically about the qualities
of the subject you're featuring"에 대응. LLM이 상품 속성(소재, 색상, 핏, 가격대,
용도, 계절)을 입력받아 상품별 고유 의견 1-2문장을 생성한다.

예시:
- "이 가격에 이 원단은 솔직히 놀랍습니다"
- "색감이 화면보다 실물이 더 좋아요"
- "건성 피부인 저한테는 이 보습력이 딱이었어요"

이 문장은 TTS로 음성화되어 영상 중간에 삽입되며, 단순 사실 나열이 아닌
체험적 어조를 사용하여 '의견/평가' 성격을 갖도록 한다.

#### Layer 9: Structural Variation (engine/structural_variation.py) ★신규

영상 구조 자체를 4가지 패턴으로 분기:

| 패턴 | 순서 | 특징 |
|------|------|------|
| 표준형 | 인트로 → 상품소개 → 가격 → 의견 → CTA | 기본 |
| 역순 가격형 | 가격(충격) → 상품소개 → 의견 → CTA | 가격 임팩트 |
| 질문 시작형 | 질문 → 상품소개 → 가격 → 의견 → CTA | 호기심 유발 |
| 비교 시작형 | 대안 제시 → 상품 비교 → 의견 → CTA | 비교 심리 |

각 패턴의 JSON 정의 파일을 templates/structural_patterns/에 저장.

#### Layer 10: Cross-Video Dissimilarity Checker (engine/cross_video_checker.py) ★신규

업로드 직전에 최근 20개 업로드 영상과 현재 영상을 3가지 지표로 비교:

| 지표 | 라이브러리 | 임계값 |
|------|------------|--------|
| 프레임 해시 | pHash (imagehash) | 유사도 < 0.85 |
| 오디오 핑거프린트 | Chromaprint (pyacoustid) | 유사도 < 0.85 |
| 텍스트 유사도 | TF-IDF (scikit-learn) | 코사인 유사도 < 0.85 |

3개 지표 중 하나라도 0.85 이상이면 자동 재생성. 재생성 시 Layer 1-9를
다른 조합으로 재실행.

### 3.4 SaaS 다중 사용자 충돌 회피 (engine/collision_avoidance.py) ★신규

동일 상품을 2명 이상 사용자가 동시 생성 요청 시:
1. Queue에서 product_id 기준 중복 감지
2. 각 사용자에게 서로 다른 스크립트 아키타입 + 시각 레이아웃 + TTS 보이스 조합을
   강제 배정
3. Cross-Video Dissimilarity Check를 사용자 간에도 적용

---

## 4. 요금제 설계

### 4.1 플랜 비교

| | Free | Starter | Pro | Business |
|--|------|---------|-----|----------|
| **월가격** | 0원 | 29,000원 | 79,000원 | 190,000원 |
| **영상/월** | 10 | 90 | 300 | 900 |
| **채널 수** | 1 | 1 | 3 | 10 |
| **TTS** | Edge-TTS | Google Cloud | ElevenLabs | ElevenLabs |
| **양산형 회피** | 기본 5-Layer | 전체 10-Layer | 전체 10-Layer | 전체 10-Layer |
| **자동 업로드** | ❌ | ✅ | ✅ | ✅ |
| **다국어** | ❌ | ❌ | 15언어 | 15언어 |
| **멀티플랫폼** | YouTube만 | YouTube만 | YT+TT+IG | YT+TT+IG |
| **상품 추천 AI** | ❌ | ❌ | ✅ | ✅ |
| **API 접근** | ❌ | ❌ | ❌ | ✅ |
| **팀 멤버** | 1 | 1 | 3 | 5 |
| **워터마크** | ShortFlow | 제거 | 제거 | 커스텀 |

### 4.2 수익 시뮬레이션

| 시점 | Free | Starter | Pro | Business | 월 매출 |
|------|------|---------|-----|----------|---------|
| 1개월 | 20 | 10 | 0 | 0 | 290,000원 |
| 3개월 | 50 | 30 | 5 | 0 | 1,265,000원 |
| 6개월 | 100 | 50 | 15 | 2 | 2,815,000원 |
| 12개월 | 200 | 100 | 40 | 5 | 7,070,000원 |

자체 채널(템빨신상맨) 예상 수익 별도:
- 월 90건 업로드, 평균 5,000회/영상 = 450,000회/월
- 쿠팡 수수료: 전환율 0.5% × 평균 주문 30,000원 × 3% = ~200,000원/월
- AdSense (1,000구독 달성 후): 450,000회 × 60원/1,000회 = ~27,000원/월
- 합계: ~227,000원/월 (SaaS 매출 전 캐시플로우 보조)

### 4.3 YouTube API 할당량 설계

기본 할당량: 일일 10,000 units, 업로드 1건 = 1,600 units → 최대 6건/일.

SaaS 확장 시 사용자별 OAuth 토큰 분산:
- 각 사용자가 자신의 YouTube 채널을 OAuth로 연결
- 업로드는 사용자의 토큰으로 실행 → 할당량이 사용자의 Google Cloud 프로젝트에 귀속
- ShortFlow 서버는 대리 업로드만 수행, 자체 할당량 소모 없음
- 사용자 수 증가에 따른 할당량 병목 해소

---

## 5. 경쟁사 분석 및 우위 전략

### 5.1 경쟁사 상세 비교

| 항목 | Reelbox | 패스트컷 | 오토판다 | ShortFlow |
|------|---------|----------|----------|-----------|
| **유형** | SaaS (크레딧) | SaaS (플랜) | 프로그램 판매 | SaaS (정액) |
| **가격** | ~$39/월 (크레딧) | 19,900-59,900원/월 | 일회성 390,000원 | 0-190,000원/월 |
| **영상/월** | 300 (크레딧 소모) | 50-120 (플랜별) | 무제한 | 10-900 (플랜별) |
| **AI 스크립트** | Claude/GPT/DeepSeek | 자체 AI | 자체 | Claude/GPT + 7 아키타입 |
| **TTS** | 자체 | 44-134종 보이스 | 자체 | 3-Stage (ElevenLabs→GCP→Edge) |
| **양산형 회피** | ❌ | ❌ | ❌ | ✅ 10-Layer |
| **다국어** | ❌ | ❌ | ❌ | ✅ 15언어 |
| **멀티플랫폼** | YouTube | YouTube | YouTube | YT + TT + IG |
| **상품 추천** | ❌ | ❌ | ❌ | ✅ AI 추천 |
| **수익 대시보드** | ❌ | ❌ | ❌ | ✅ |
| **자동 업데이트** | ✅ (SaaS) | ✅ (SaaS) | ❌ (로컬) | ✅ (SaaS) |
| **YouTube 정책 대응** | 없음 | 없음 | 없음 | 10-Layer + 실시간 모니터링 |

### 5.2 후발주자 5대 경쟁우위 전략

**전략 1: "채널 수호자" 포지셔닝**

2026-01 기준 AI 채널 16% 삭제. "영상을 만들어주는 서비스"가 아닌
"채널을 지켜주는 서비스"로 포지셔닝. 10-Layer 엔진(3,125 시각 조합 × 7 아키타입
× 4 구조 패턴)과 Cross-Video Dissimilarity Checker를 마케팅 전면에 배치.

핵심 메시지: "다른 도구는 영상만 만들어줍니다. ShortFlow는 당신의 채널을 지킵니다."

**전략 2: 투명 정액제 가격 파괴**

Reelbox 크레딧 불투명(실 사용량 예측 불가), 오토판다 일회성 39만원(업데이트 불가),
패스트컷 프로 46,900원/80개 대비 ShortFlow Starter 29,000원/90개는
가격 36% 저렴 + 영상 수 12.5% 추가.

**전략 3: 즉시 체험 PLG(Product-Led Growth) 퍼널**

가입 없이 쿠팡 URL 1개 입력 → 3분 내 워터마크 포함 샘플 영상 생성 → 회원가입 유도
→ Free(10건/월) → Starter 전환. 경쟁사 중 no-signup demo 제공 업체 없음.

**전략 4: 수익 최적화 AI 추천 대시보드**

쿠팡 베스트셀러·실시간 랭킹 크롤링 → 카테고리별 수수료율·예상 조회수·전환율
가중치 산출 → 상위 5개 상품 자동 추천. "영상 제작 도구"에서 "수익 최적화 플랫폼"으로
포지셔닝 전환.

**전략 5: 멀티플랫폼 + 다국어**

YouTube + TikTok + Instagram Reels 동시 배포, 플랫폼별 메타데이터 자동 변환.
15개 언어(KR, EN, ZH-CN, ZH-TW, JA, AR, TH, VI, ID, ES, PT, HI, FR, DE, RU)
자동 번역.

---

## 6. 제목 전략 및 글로벌 SEO

### 6.1 한국어 제목 템플릿

`[숫자]가지 + [감정트리거] + [플랫폼(쿠팡/올영)] + #Shorts`

감정 트리거 키워드: 미친, 끝판왕, 모르면 손해, 역대급, 충격, 이건 사야 해,
진심 추천, 가성비 갑.

### 6.2 15개 언어 키워드 전략

각 시장별 검색량 상위 키워드를 사전 매핑하여, 번역 시 직역이 아닌
현지 SEO 최적화 키워드로 대체.

---

## 7. 운영 스케줄

### 7.1 일간

| 시간 | 작업 | 템플릿 |
|------|------|--------|
| 09:00 ±30분 | 업로드 1 | Template E (오늘의 신상) |
| 13:00 ±30분 | 업로드 2 | Template C (GRWM) |
| 18:00 ±30분 | 업로드 3 | Template B (가격쇼크) |

해당 템플릿에 대기 영상 없을 시 다른 템플릿으로 폴백.

### 7.2 주간

- 월요일: 조회수/전환율 리포트 분석
- 수요일: 저성과 상품 교체 + 10개 신규 상품 추가
- 금요일: A/B 테스트 분석 (제목/썸네일/스크립트 아키타입)
- 일요일: 다음 주 상품 DB 로드

### 7.3 월간 마일스톤

| 시점 | 목표 |
|------|------|
| 1개월 | 90 영상, 총 10,000회 |
| 2개월 | 1개 영상 10,000회 돌파, 500 구독 |
| 3개월 | 수익화 (1,000 구독), 월 1,000,000원 |
| 6개월 | 5,000 구독, 월 5,000,000원 |

---

## 8. 대시보드 설계

### 8.1 Screen 1 – Today's Status

4개 카드: (a) 오늘 업로드 현황 (예: "3/3 슬롯 완료"), (b) 총 조회수 (YouTube API),
(c) 이번 달 누적 업로드, (d) 시스템 헬스 (n8n, Docker, 디스크) – 신호등 컬러.
하단: 3개 슬롯 타임라인 (상품, 썸네일, 길이, YouTube 링크, 시간, 상태).

### 8.2 Screen 2 – Video Performance

필터: 오늘/7일/30일/전체. 테이블: 업로드일, 상품, 카테고리, 조회수, 좋아요,
댓글, 시청 시간 %, 쿠팡 클릭수. 정렬 가능. 상단: 카테고리별 평균 조회수 바 차트.

### 8.3 Screen 3 – Product Management

Supabase products 리스트, 상태 필터 (pending/processing/completed/failed).
실패 행 빨간색 하이라이트 + 재시도 버튼. 상품 추가 모달 + 쿠팡 인기 상품
자동 추천(engine/product_recommender.py).

### 8.4 Screen 4 – System Monitoring

Docker 컨테이너 상태 (worker, n8n, api, dashboard) + CPU/Memory.
n8n 최근 워크플로우 실행 목록. TTS 사용량 (ElevenLabs 크레딧, GCP TTS 호출수).
YouTube API 할당량 게이지 (10,000 중 잔여). 최근 10건 에러 로그.
DEAD_LETTER 큐 카운트.

### 8.5 Screen 5 – Revenue Tracking (Phase 2 이후)

쿠팡 API 승인 후 활성화. 일간/주간/월간 클릭·전환·수익 차트.
영상별 수익 랭킹. 월 목표 대비 진행률 프로그레스 바.

### 8.6 기술 구현

- Frontend: Next.js + Tailwind + Alpine.js, 모바일 반응형
- Backend: FastAPI (Python) – /api/v1/products, /jobs, /channels, /analytics,
  /pipeline/trigger, /recommendations
- 갱신 주기: 메인 카드 30초, 성과 데이터 1시간, 시스템 메트릭 1분
- 보안: DASHBOARD_PASSWORD 환경변수 또는 IP 화이트리스트 (포트 3000)

---

## 9. 파일 구조

```
/data/shortflow/
├── docs/
│   ├── shortflow_v3.0_plan.md
│   ├── styleflow_v1.0_plan.md
│   ├── anti_inauthentic_spec.md
│   ├── competitive_analysis.md
│   └── legal_checklist.md
├── docker-compose.yml
├── .env
├── .cursorrules
├── .gitignore
├── requirements.txt
├── credentials/
├── engine/
├── worker/
├── api/
├── dashboard/
├── scripts/
├── templates/
├── sql/
├── data/
└── logs/
```

---

## 10. 환경변수 (.env)

```bash
# === Database (MySQL - NewTalk) ===
NEWTALK_DB_HOST=localhost
NEWTALK_DB_NAME=autoda
NEWTALK_DB_USER=pigupuser
NEWTALK_DB_PASSWORD=

# === Supabase ===
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# === YouTube ===
YOUTUBE_CHANNEL_ID=UCqpf3lJQio6EBHxthLQob0g
YOUTUBE_CLIENT_SECRET_PATH=/app/credentials/youtube_client_secret.json
YOUTUBE_TOKEN_PATH=/app/credentials/youtube_token.json
YOUTUBE_DEFAULT_PRIVACY=public
YOUTUBE_DAILY_LIMIT=6

# === TTS ===
TTS_PROVIDER=google-cloud
GOOGLE_TTS_VOICE=ko-KR-Chirp3-HD-Kore
GOOGLE_TTS_KEY_PATH=/app/credentials/gcloud-tts-key.json
ELEVENLABS_API_KEY=

# === LLM ===
LLM_MODEL=claude-opus-4-6
LLM_API_KEY=

# === Video Settings ===
DEFAULT_VIDEO_WIDTH=1080
DEFAULT_VIDEO_HEIGHT=1920
DEFAULT_VIDEO_FPS=29.97
DEFAULT_VIDEO_CODEC=libx264
DEFAULT_AUDIO_CODEC=aac
DEFAULT_AUDIO_RATE=44100

# === 양산형 회피 엔진 ===
ORIGINALITY_THRESHOLD=70
CROSS_VIDEO_SIMILARITY_THRESHOLD=0.85
UPLOAD_OFFSET_MINUTES=30

# === Pipeline ===
AUTO_UPLOAD=true
MAX_RETRY=3
DEAD_LETTER_ENABLED=true

# === Dashboard ===
DASHBOARD_PASSWORD=
DASHBOARD_PORT=3000
```

---

## 11. 의존성 (requirements.txt)

```
fastapi>=0.104.0
uvicorn>=0.24.0
supabase>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-api-python-client>=2.0.0
openai>=1.0.0
anthropic>=0.18.0
edge-tts>=6.1.0
elevenlabs>=0.3.0
google-cloud-texttospeech>=2.14.0
ffmpeg-python>=0.2.0
Pillow>=10.0.0
imagehash>=4.3.0
pyacoustid>=1.2.0
scikit-learn>=1.3.0
python-dotenv>=1.0.0
watchdog>=3.0.0
mysqlclient>=2.2.0
redis>=5.0.0
requests>=2.31.0
schedule>=1.2.0
```

FFmpeg 4.2.7+ 시스템 설치 필요.

---

## 12. 리스크 관리

| 리스크 | 심각도 | 발생확률 | 대응 |
|--------|--------|----------|------|
| YouTube 양산형 수익 정지 | 치명적 | 높음 | 10-Layer 엔진 + 창작성 점수 차단 |
| YouTube 정책 추가 강화 | 높음 | 중간 | 자동 모니터링 + 파라미터 실시간 조정 |
| 쿠팡 파트너스 약관 변경 | 높음 | 낮음 | 멀티 제휴처 분산 (네이버, 11번가) |
| 쿠팡 제3자 SaaS 약관 불확실 | 높음 | 중간 | Phase 3 전 서면 문의 + Reelbox 선례 확인 |
| 경쟁사 기능 복제 | 중간 | 중간 | 선점 효과 + 데이터 축적 고도화 |
| SaaS 사용자 간 영상 유사성 | 중간 | 높음 | Collision Avoidance Protocol |
| TTS 과금 급증 | 낮음 | 중간 | Edge-TTS 폴백 + 로컬 TTS 검토 |
| 서버 장애 | 높음 | 낮음 | Docker 자동 재시작 + DLQ + DR 계획 |
| 통신판매업 미신고 | 높음 | - | Phase 3 전 반드시 완료 |

---

## 13. 법률·약관 체크리스트

| 항목 | 상태 | 기한 | 비고 |
|------|------|------|------|
| 쿠팡 파트너스 약관 제3자 SaaS 허용 확인 | ⬜ 미완료 | Phase 3 전 | 서면 문의 |
| Reelbox 선례 법적 성격 확인 | ⬜ 미완료 | Phase 2 중 | 명시허가 vs 묵인 |
| 통신판매업 신고 | ⬜ 미완료 | Phase 3 전 | 유료 서비스 전환 조건 |
| 전자상거래법 청약철회 7일 | ⬜ 미완료 | Phase 3 전 | 약관에 반영 |
| 상품 이미지 저작권 | ⬜ 미완료 | Phase 2 중 | AI 생성 이미지 사용 |
| YouTube ToS 준수 | ✅ 반영 | - | 10-Layer 엔진 |
| 개인정보처리방침 | ⬜ 미완료 | Phase 3 전 | SaaS 회원 정보 |

---

## 14. 로드맵

### Phase 1: 내부 도구 구축 (0-2주) ← 현재

- Sprint 1: 10-Layer 양산형 회피 엔진 코어 구현
- Sprint 2: 대시보드 백엔드 API (FastAPI + Supabase)
- Sprint 3: 대시보드 프론트엔드 (Next.js)
- Sprint 4: 파이프라인 통합 (pipeline_worker + originality scorer)
- 대표 계정 1개로 전체 파이프라인 검증

### Phase 2: 클로즈드 베타 (3-4주)

- 회원가입·로그인 (Supabase Auth)
- 베타 테스터 5-10명 모집
- Free 요금제 운영
- 법률 확인 병행 (쿠팡 약관, 통신판매업)

### Phase 3: 퍼블릭 베타 (5-8주)

- 유료 전환 (Starter/Pro)
- 결제 연동 (토스페이먼츠 정기결제)
- 쿠팡 인기 상품 자동 추천 기능 출시
- 통신판매업 신고 완료

### Phase 4: 스케일업 (2-3개월)

- Business 요금제 + API 공개
- 멀티플랫폼 (TikTok, Instagram Reels)
- 워커 수평 확장 (Redis 큐)
- 15개 언어 글로벌 SEO
- B2B 영업 시작

---

## 15. 기술 스택 요약

| 영역 | 기술 |
|------|------|
| Frontend | Next.js 14 + Tailwind CSS + Alpine.js |
| Backend API | FastAPI (Python 3.11) |
| Database | Supabase (PostgreSQL + Auth + RLS + Realtime) |
| 기존 DB | MySQL/MariaDB (autoda) |
| 결제 | 토스페이먼츠 정기결제 API |
| 인증 | Supabase Auth (JWT) + Google OAuth |
| 영상 처리 | FFmpeg 4.2.7 + ffmpeg-python |
| AI/LLM | Claude Opus 4.6 / GPT-4o |
| TTS | ElevenLabs / Google Cloud TTS / Edge-TTS |
| 스케줄러 | n8n (Docker) |
| 큐 | Redis (Phase 3) |
| 컨테이너 | Docker Compose |
| 모니터링 | 자체 대시보드 + 로그 (/data/styleflow/logs/) |

---

## 16. 핵심 URL

| 용도 | URL |
|------|-----|
| **SaaS 대시보드 (공식)** | https://shotflow.newtalk.kr |
| YouTube 채널 | https://www.youtube.com/channel/UCqpf3lJQio6EBHxthLQob0g |
| 릴스 미리보기 (데모) | http://114.207.244.86:8888/index.html |
| 대시보드 (IP 직접) | http://114.207.244.86:3000 |
| YouTube Data API v3 | https://www.googleapis.com/youtube/v3/videos |
| 쿠팡 파트너스 | https://partners.coupang.com |
| Supabase | (프로젝트 생성 후 기입) |
| n8n | http://114.207.244.86:5678 |

---

## 17. 액션 항목

| # | 작업 | 담당 | 상태 | 우선순위 |
|---|------|------|------|----------|
| 1 | 10-Layer 양산형 회피 엔진 구현 | 개발 | ⬜ | ★★★ |
| 2 | 대시보드 백엔드 API 구축 | 개발 | ⬜ | ★★★ |
| 3 | 대시보드 프론트엔드 구축 | 개발 | ⬜ | ★★★ |
| 4 | Supabase 스키마 배포 | 개발 | ⬜ | ★★★ |
| 5 | DB 비밀번호 .env 설정 | 개발 | ⬜ | ★★★ |
| 6 | crontab NAS 동기화 등록 | 개발 | ⬜ | ★★☆ |
| 7 | YouTube OAuth 완료 | 대표 | ⬜ | ★★☆ |
| 8 | Google Cloud 프로젝트 생성 | 대표 | ⬜ | ★★☆ |
| 9 | 쿠팡 파트너스 약관 서면 확인 | 대표 | ⬜ | ★★☆ |
| 10 | 통신판매업 신고 | 대표 | ⬜ | ★★☆ |
| 11 | BGM 라이브러리 30곡 확보 | 개발 | ⬜ | ★★☆ |
| 12 | 15개 언어 번역 세팅 | 개발 | ⬜ | ★☆☆ |
| 13 | TikTok/Instagram API 연동 | 개발 | ⬜ | ★☆☆ |
| 14 | 토스페이먼츠 결제 연동 | 개발 | ⬜ | ★☆☆ |

---

## 부록 A: .cursorrules 파일

별도 파일 /data/shortflow/.cursorrules 참조.

## 부록 B: Supabase 스키마 전문

별도 파일 /data/shortflow/sql/supabase_schema.sql 참조.

---

> **문서 끝 – ShortFlow v3.0 기획서**
> 최종 수정: 2026-02-22
