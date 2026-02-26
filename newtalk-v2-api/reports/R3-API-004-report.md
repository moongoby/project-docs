# R3-API-004 작업 보고서
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-004 |
| 작업명 | DM API (1:1 대화, 메시지, 읽음 처리) |
| 버전 | v2.7.0 |
| 상태 | 완료 |
| Git SHA | 8f7fece |

## 구현
- **conversations** 테이블: type(direct/group), title, last_message_id, last_message_at, metadata, softDeletes
- **conversation_participants** 테이블: conversation_id, user_id, role(owner/member), is_muted, is_pinned, last_read_at, joined_at, left_at
- **messages** 테이블: conversation_id, sender_id, type(text/image/product/order/system), body, metadata, is_deleted
- **message_reads** 테이블: message_id, user_id, read_at
- Conversation, ConversationParticipant, Message, MessageRead 모델
- ConversationService, MessageService
- ConversationController 6 EP, MessageController 4 EP (총 10 엔드포인트)
- 메시지 타입: text, image, product, order, system
- 읽음 처리: participant.last_read_at + message_reads 이중 추적
