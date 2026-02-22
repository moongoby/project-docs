# GO100 기획서
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 1. 서비스 비전
- GO100: AI 기반 주식 자동매매 SaaS
- 핵심 가치: AI가 전략을 설계, 백테스트, 자동매매까지 원스톱
- 타겟: 주식 투자에 관심있으나 전문 지식 부족한 개인 투자자
- V4.1 코드베이스 공유, 도메인 분리 운영

## 2. 핵심 기능
### 2.1 AI 전략 설계 (백억이)
- 자연어 대화로 투자 전략 생성
- 플로팅 위젯 (모든 화면) + 전체화면 (/llm)
- 자동 전략명/설명 생성, 조건 추출
- go100_strategy_cards 직접 저장

### 2.2 전략카드 시스템
- 전체 전략: 관리자 featured 지정 (마켓플레이스 확장 예정)
- 내 전략: 사용자 개인 전략
- 카드 상세 모달, 활성/비활성 토글, 검색

### 2.3 백테스트
- GO100: universe_filter 자동 종목 선정
- 결과: 수익률, MDD, 샤프비율

### 2.4 자동매매
- KIS API (한국투자증권) 연동
- 실거래 / 모의거래

### 2.5 마켓플레이스 (Phase 4 예정)
- 전략 공유/구독, is_featured/is_public 관리자 큐레이션

## 3. 사용자 플로우
### 3.1 전략 생성
백억이 대화 → AI 조건 설계 → 전략카드 저장 → 내전략 확인 → 백테스트 → 활성화 → 자동매매

### 3.2 전략카드 관리
전략카드 페이지 → 전체전략/내전략 탭 → 상세 모달 → 토글/검색

## 4. 페이지 구조
| 경로 | 기능 | 상태 |
|------|------|------|
| / | 루트 | 완료 |
| /auth/login | 로그인 | 완료 |
| /auth/signup | 회원가입 | 완료 |
| /auth/forgot-password | 비밀번호 찾기 | 완료 |
| /auth/callback | 소셜 콜백 | 완료 |
| /(protected)/dashboard | 대시보드 | 완료 |
| /(protected)/strategy-cards | 전략카드 (전체/내전략) | 완료 |
| /(protected)/llm | 백억이 대화 전체화면 | 완료 |
| /(protected)/backtest | 백테스트 | 완료 |
| /(protected)/go100 | GO100 대시 | 완료 |
| /(protected)/go100/chat | GO100 채팅 | 완료 |
| /(protected)/go100/strategies | GO100 전략 목록 | 완료 |
| /(protected)/go100/strategies/[id] | GO100 전략 상세 | 완료 |
| /(protected)/go100/paper-trading | 모의거래 | 완료 |
| /(protected)/go100/paper-trading/[id] | 모의거래 상세 | 완료 |
| /(protected)/go100/live-trading | 실거래 | 완료 |
| /(protected)/go100/live-trading/[id] | 실거래 상세 | 완료 |
| /(protected)/go100/store | 스토어 | 완료 |
| /(protected)/go100/settings | GO100 설정 | 완료 |
| /(protected)/accounts | 계좌 | 완료 |
| /(protected)/portfolio | 포트폴리오 | 완료 |
| /(protected)/trade | 거래 | 완료 |
| /(protected)/reports | 리포트 | 완료 |
| /(protected)/notifications | 알림 | 완료 |
| /(protected)/settings | 설정 | 완료 |
| /(protected)/admin | 관리자 | 완료 |
| /(protected)/monitoring | 모니터링 | 완료 |
| /terms | 이용약관 | 완료 |
| /privacy | 개인정보처리방침 | 완료 |
| /offline | 오프라인 | 완료 |

## 5. 수익 모델 (계획)
- SaaS 월 구독
- 마켓플레이스 수수료
- 프리미엄 AI 기능
