# CUR-V41-STRATEGY-CARDS-COUNT-DIAG-001 — strategy_cards 60건 원인 진단

- **일시**: 2026-02-23 20:00 KST
- **서버**: root@[SERVER-IP]
- **절대규칙 준수**: 읽기 전용(SELECT only), DB/코드 변경 없음, kis-v41-* 재시작 금지

---

## 1. 요약

| 구분 | 내용 |
|------|------|
| **진단 결과** | **CASE B**: card_id 1~62 중 **빈 번호 2개** (2, 4). 원래 62건이었으나 해당 2개는 과거에 비어 있었고, 63~67 추가 후 65건이었다가 63~67 삭제로 **현재 60건** |
| **전체 건수** | 60건 |
| **빈 card_id** | 2, 4 |
| **시퀀스 현재값** | 67 (last_value=67, is_called=t) |
| **CONTEXT.md 갱신 권고** | 기준값을 **60**으로 갱신 권고. 또는 62(실제 60, card_id 2·4 비어 있음) 명시 |
| **DB 변경** | 없음 |

---

## 2. card_id 전체 목록 (60건)

| card_id | strategy_name | desk_id | is_active |
|---------|---------------|---------|-----------|
| 1 | 볼린저 밴드 돌파 | (NULL) | f |
| 3 | # 🚀 GO100 추세 상승 극대화 전략… | (NULL) | t |
| 5 | DESK1_스캘핑_class_b | 1 | t |
| 6 | DESK2_데일리_class_a | 2 | t |
| 7 | DESK2_종가매매_class_c | 2 | t |
| 8 | DESK3_단기스윙_class_d | 3 | t |
| 9 | DESK4_중기스윙_class_e | 4 | t |
| 10 | DESK5_장기스윙_class_f | 5 | t |
| 11~60 | (DESK1~5 전략들) | 1~5 | t |
| 61 | 시초가매매 | (NULL) | t |
| 62 | 제시해주신 조건들을 바탕으로… | (NULL) | t |

- **비어 있는 card_id (1~62 구간)**: **2, 4**

---

## 3. 빈 card_id 번호 (1~62 기준)

```text
 missing_card_id
-----------------
               2
               4
(2 rows)
```

---

## 4. 집계

| 항목 | 값 |
|------|-----|
| total | 60 |
| min_id | 1 |
| max_id | 62 |
| desk_count | 5 |

---

## 5. DESK별 카드 수

| desk_id | card_count | active_count |
|---------|------------|--------------|
| 1 | 10 | 10 |
| 2 | 16 | 16 |
| 3 | 11 | 11 |
| 4 | 9 | 9 |
| 5 | 10 | 10 |
| (NULL) | 4 | 3 |

- desk_id NULL: card_id 1, 3, 61, 62 (비 DESK 할당 카드)

---

## 6. 시퀀스 현재값

```text
 last_value | is_called
------------+-----------
         67 | t
```

- **해석**: 마지막 INSERT로 사용된 card_id가 67까지 진행됨. GO100 테스트 카드 63~67 삭제 후에도 시퀀스는 67로 유지됨.

---

## 7. 삭제/이력 참고

- **백업 덤프**: `/tmp/backup_strategy_cards_before_cleanup_20260223_172910.dump` 존재 (삭제 전 백업).
- **git log**: strategy_cards 관련 INSERT/매핑 커밋 다수. DELETE는 지시서에서 언급된 63~67 수동 삭제(커밋 미포함 가능).

---

## 8. CONTEXT.md 기준값 갱신 권고

- **현재 CONTEXT.md**: strategy_cards = 62건
- **실제**: 60건 (card_id 2·4 비어 있음, 63~67 삭제 반영)
- **권고**:
  1. **옵션 A**: CONTEXT.md·kis-v41-rules.md의 무결성 기준값을 **60**으로 변경.
  2. **옵션 B**: 62를 유지할 경우 `strategy_cards: 62(실제 60, card_id 2·4 비어 있음)` 형태로 명시.

---

## 9. 결론

- **원인**: card_id 1~62 중 **2, 4번이 비어 있음**. 63~67 추가로 한때 65건이었다가, 63~67 삭제 후 **60건**이 맞음.
- **DB 변경**: 없음 (진단만 수행).
- **다음 단계**: CEO 결정에 따라 CONTEXT.md 기준값 60으로 갱신 또는 62(실제 60) 명시.
