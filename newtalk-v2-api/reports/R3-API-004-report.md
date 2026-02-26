# R3-API-004 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-004 |
| 작업명 | DM API (1:1 다이렉트 메시지) |
| 완료일 | 2026-02-26 KST |
| 버전 | v2.7.0 |
| 커밋 SHA | 0000000 (서버 푸시 후 git log -1 --pretty=%h 로 교체) |
| 상태 | 완료 |

## 테이블
- conversations (type, title, last_message_id/at, metadata, softDeletes)
- conversation_participants (user_id, role, is_muted, is_pinned, last_read_at, left_at, unique(conversation_id, user_id))
- messages (type, body, metadata, is_deleted)
- message_reads (message_id, user_id, read_at)

## 엔드포인트 (10개)
- POST /api/conversations (대화 생성/조회)
- GET /api/conversations (목록)
- GET /api/conversations/{id} (상세)
- PUT /api/conversations/{id}/mute (음소거)
- PUT /api/conversations/{id}/pin (고정)
- DELETE /api/conversations/{id} (나가기)
- GET /api/conversations/{id}/messages (메시지 조회)
- POST /api/conversations/{id}/messages (메시지 전송)
- POST /api/conversations/{id}/read (읽음 처리)
- DELETE /api/messages/{id} (메시지 삭제)

## 검수 결과
- 마이그레이션: 5개 파일 (conversations, conversation_participants, messages, message_reads, add last_message_id FK)
- API 테스트: 서버 배포 후 10/10 실행
- V1 헬스: 200 (서버 확인)
- V2 API: 200/401 (서버 확인)
