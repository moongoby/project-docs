# KIS AutoTrade V4.1 — 작업 보고서

Cursor 작업 완료 보고서가 저장되는 디렉토리.

## 파일명 규칙

```
작업명-YYYYMMDD.md
```

예시:
- MINUTE-COLLECTOR-STATUS-20260223.md
- DESK2-MINUTE-REBT-20260224.md
- KIS-DOCS-FULL-SETUP-20260223.md

## 보안 규칙

보고서에 다음 정보를 절대 포함하지 않는다:
- API 키, 비밀번호, 인증 토큰
- 계좌번호
- .env 파일 내용
- 서버 접속 credentials

## 활용

CEO가 Claude에게 아래 형식으로 URL을 전달하면
Claude가 직접 읽고 분석한다:

```
보고서 확인:
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/작업명-날짜.md
```
