# LLM 엔진 Gemini 전환 보고서

**작성일시:** 2026-02-24 16:00 KST  
**작업 유형:** 신규 개발 / 리팩터링  
**상태:** 완료  
**서버:** [SERVER-HOSTNAME] ([SERVER-IP])  
**프로젝트:** /data/shortflow  

## 1. 작업 개요
기존 Anthropic/OpenAI 이중 엔진을 Google Gemini 우선 3중 엔진으로 전환.  
Gemini 2.0 Flash의 무료 티어 + JSON 네이티브 출력 활용.

## 2. 프로바이더 우선순위

| 순위 | 프로바이더 | 모델 | 비용 | 비고 |
|------|-----------|------|------|------|
| 1 | Google Gemini | gemini-2.0-flash | 무료 티어 넉넉 | response_mime_type=json |
| 2 | OpenAI | gpt-4o | 유료 | 폴백 |
| 3 | Anthropic | claude-sonnet-4 | 유료 | 폴백 |

## 3. 변경 사항

| 파일 | 변경 내용 |
|------|----------|
| engine/llm_script_engine.py | v3.0 - Gemini 우선 3중 엔진 |
| scripts/generate_content_script.py | GEMINI_API_KEY 로드, LLM_PRIMARY에 gemini 추가 |
| engine/requirements.txt | google-generativeai, openai, anthropic 명시 |
| requirements: google-generativeai | venv에 설치 완료 |

## 4. 테스트 결과

| 테스트 | 결과 |
|--------|------|
| import 확인 | ✅ |
| dry-run 3채널 (economy, health, history) | ✅ |
| Gemini API 호출 (economy 1건) | GEMINI_API_KEY 설정 후 STEP 6 재실행 |
| Gemini API 호출 (health 1건) | 동일 |
| Gemini API 호출 (history 1건) | 동일 |
| JSON 구조 검증 | 생성 후 output/scripts/{channel}/*.json 검증 |

## 5. 환경변수
- **GEMINI_API_KEY**: .env에 추가 필요 (Google AI Studio에서 발급)  
  - 발급: https://aistudio.google.com/app/apikey → Create API key  
  - 추가: `echo "GEMINI_API_KEY=발급받은키" >> /data/shortflow/.env`
- **LLM_PRIMARY**: 선택. `gemini`(기본), `openai`, `anthropic` 중 택 1. 미설정 시 키 존재 순서로 primary 결정.

## 6. 백업
- 경로: `/data/shortflow/backups/20260224_160000_gemini_switch/`
- 파일: `llm_script_engine.py.bak`, `generate_content_script.py.bak`

## 7. 검수 요약
- 3중 프로바이더: `_call_gemini`, `_call_openai`, `_call_anthropic` 구현 확인
- Gemini 모델명: `gemini-2.0-flash`
- `response_mime_type=application/json` (Gemini 전용, 구버전 SDK는 dict 폴백)
- 폴백 순서: `try_order` = primary → 나머지
- 면책 고지: 건강/경제 채널 disclaimer 필드 강제

## 8. 다음 작업
- .env에 GEMINI_API_KEY 추가 후 `python3 scripts/generate_content_script.py --channel economy --subject "2026 부동산 전망 3가지"` 로 1건 실호출 테스트
- 3채널 배치 테스트 (각 3편)
- 생성된 대본 → ShortFlow 영상 파이프라인 연결
- 업로드 스케줄러(cron) 연동
