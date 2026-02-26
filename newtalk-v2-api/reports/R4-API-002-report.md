# R4-API-002 보고서: 스토리 API

**문서번호**: R4-API-002  
**작성일시**: 2026-02-26 KST  
**버전**: v3.2.0  
**참조**: R4-API-002 작업 지시서, NT-V2-ARCHITECTURE

---

## §1. 개요

24시간 한정 스토리 콘텐츠. 도매가 업로드 → 소매가 팔로우 기반으로 시청. 인스타그램 스토리와 유사한 UX.

---

## §2. 생성·수정된 파일 목록

### 마이그레이션 (database/migrations/)
| 구분 | 경로 |
|------|------|
| 신규 | 2026_02_26_310001_create_stories_table.php |
| 신규 | 2026_02_26_310002_create_story_views_table.php |

### 모델 (app/Models/)
| 구분 | 경로 |
|------|------|
| 신규 | Story.php |
| 신규 | StoryView.php |

### 서비스 (app/Services/)
| 구분 | 경로 |
|------|------|
| 신규 | StoryService.php (11 메서드) |

### 컨트롤러 (app/Http/Controllers/Api/)
| 구분 | 경로 |
|------|------|
| 신규 | StoryController.php (10 엔드포인트) |

### 콘솔 (app/Console/Commands/)
| 구분 | 경로 |
|------|------|
| 신규 | StoryCleanupExpiredCommand.php (story:cleanup-expired) |

### 라우트·스케줄
| 구분 | 경로 |
|------|------|
| 수정 | routes/api.php (R4-API-002 스토리 라우트 추가) |
| 신규 | routes/console.php (매시 만료 정리 스케줄) |

---

## §3. 테이블 스키마

### stories
- id, user_id(FK), media_type(image|video), media_url, thumbnail_url, caption, link_url, link_type(product|brand|external|none), link_id, view_count, reply_count, is_highlight, expires_at, timestamps, softDeletes
- 인덱스: (user_id, expires_at), (expires_at, created_at), (user_id, is_highlight)

### story_views
- id, story_id(FK CASCADE), user_id(FK), viewed_at, reaction(none|like|fire|clap|wow|sad), timestamps
- unique(story_id, user_id), index(user_id, viewed_at)

---

## §4. StoryService 메서드 (11개)

| 메서드 | 설명 |
|--------|------|
| create(userId, data) | 스토리 업로드, expires_at = now + 24h |
| getFeed(userId) | 팔로우 중인 사용자 활성 스토리, 사용자별 그룹핑, 읽음 여부 |
| getUserStories(userId) | 특정 사용자 활성 스토리 |
| getMyStories(userId) | 내 스토리 (활성+만료) |
| view(storyId, userId) | 조회 기록, 중복 방지, view_count 증가 |
| react(storyId, userId, reaction) | 리액션 업데이트 |
| getViewers(storyId) | 조회자 목록 (작성자만) |
| delete(storyId, userId) | 삭제 (본인 확인) |
| getHighlights(userId) | 하이라이트 스토리 |
| toggleHighlight(storyId, userId) | 하이라이트 토글 |
| cleanupExpired() | 만료 스토리 소프트삭제 (스케줄러용) |

---

## §5. 엔드포인트 (10개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /api/stories | 스토리 업로드 |
| GET | /api/stories/feed | 스토리 피드 (팔로우 기반) |
| GET | /api/stories/user/{userId} | 특정 사용자 스토리 |
| GET | /api/stories/mine | 내 스토리 (활성+만료) |
| GET | /api/stories/{id} | 스토리 상세 |
| DELETE | /api/stories/{id} | 삭제 |
| POST | /api/stories/{id}/view | 조회 기록 |
| POST | /api/stories/{id}/react | 리액션 |
| GET | /api/stories/{id}/viewers | 조회자 목록 |
| PUT | /api/stories/{id}/highlight | 하이라이트 토글 |

---

## §6. 스케줄러

- **매시**: 만료된 스토리 소프트삭제 (StoryService::cleanupExpired)
- **방식**: routes/console.php 에 Schedule::call()->hourly()
- **수동 실행**: `php artisan story:cleanup-expired`
- Laravel 11+ 에서 bootstrap/app.php 의 withSchedule() 로 routes/console.php 를 로드하거나, cron 에서 위 아티산 커맨드를 매시 실행 권장.

---

## §7. 서버 실행 체크리스트

1. **마이그레이션**  
   `docker compose --env-file .env.docker exec app php artisan migrate --force`

2. **라우트 확인**  
   `docker compose --env-file .env.docker exec app php artisan route:list --path=stories` → 10개

3. **API 테스트**  
   - 스토리 업로드: `curl -s -X POST http://localhost:8080/api/stories -H "Authorization: Bearer $WHOLESALE_TOKEN" -H "Content-Type: application/json" -d '{"media_type":"image","media_url":"/images/test.jpg","caption":"신상 입고!"}'`
   - 피드: `curl -s http://localhost:8080/api/stories/feed -H "Authorization: Bearer $RETAIL_TOKEN"`

4. **Git 커밋·푸시**  
   `git add -A && git commit -m "[R4-API-002] 스토리 API — stories/story_views 2테이블, StoryService 11메서드, 10 엔드포인트, 스케줄러 (v3.2.0)" && git push origin main`

5. **문서 갱신**  
   CHANGELOG, CONTEXT, HANDOVER, ARCHITECTURE 갱신 후 보고서 §8 최종 보고 형식 작성.

---

## §8. 최종 보고 (완료 시 서버에서 기록)

```
R4-API-002 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━
완료 시각: {KST}
V2 repo SHA: {7자리}
project-docs SHA: {7자리}

테이블 2개: stories, story_views
모델 2개: Story, StoryView
서비스: StoryService (11 메서드)
엔드포인트 10개
스케줄러: 매시 만료 정리

문서: CONTEXT/CHANGELOG/HANDOVER/ARCHITECTURE 갱신
보고서: R4-API-002-report.md
헬스: V1 {code}, V2 API {code}, Frontend {code}
Docker: {N}/5 Up
━━━━━━━━━━━━━━━━━━━━━━━━━━
```
