# KIS API 문서 (로컬 참고용)

68서버 `webapp/docs/api/kisapi` 에 있는 엑셀 문서를 이 디렉터리로 복사하여 참고·관리합니다.

## 복사 방법 (68서버 → 현 서버)

```bash
# 68서버에서 현 서버로 rsync 예시 (호스트/경로는 환경에 맞게 수정)
rsync -avz user@68서버주소:webapp/docs/api/kisapi/ /root/kis-autotrade-v4/docs/api/kisapi/
# 또는 scp
scp user@68서버주소:webapp/docs/api/kisapi/*.xlsx /root/kis-autotrade-v4/docs/api/kisapi/
```

## 복사 대상 파일 목록 (68서버 기준)

| 파일명 | 설명 |
|--------|------|
| `[국내주식] 기본시세.xlsx` | 기본 시세 API |
| `[국내주식] 순위분석.xlsx` | 순위분석 API |
| `[국내주식] 시세분석.xlsx` | 시세분석 API |
| `[국내주식] 실시간시.xlsx` | 실시간 시세 API |
| `[국내주식] 업종_기타.xlsx` | 업종·기타 API |
| `[국내주식] 종목정보.xlsx` | 종목정보 API |
| `[국내주식] 주문_계조.xlsx` | 주문·계좌 API |
| `OAuth인증.xlsx` | OAuth 인증 스펙 |

복사 후 위 .xlsx 파일들이 이 디렉터리에 있으면 Cursor 규칙 및 Phase 2 KIS 연동 시 참고합니다.
