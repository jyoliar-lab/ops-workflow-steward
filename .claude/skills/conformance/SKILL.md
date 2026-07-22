---
name: conformance
description: accepted ADR과 피관리 하네스(docs-tickets·ticket-engineer)의 정합성 검토·교정. "하네스가 정책과 어긋났나", "정책을 하네스에 반영", "정합성 전파"일 때.
---

# conformance — 하네스 정합·전파

`accepted` 정책이 **피관리 하네스에 반영돼 있는지** 확인하고, 어긋나면 **교정**한다. 피관리 하네스는 둘이다:

- **docs-tickets** — `$OPS_WORKFLOW_ROOT/.claude/**` + `$OPS_WORKFLOW_ROOT/CLAUDE.md`
- **ticket-engineer** — `$TICKET_ENGINEER_ROOT` (저장소 전체)

둘 다 정책에 "매여" 있으므로, 그 매임의 내용을 최신 정책으로 유지하는 것이 목적. (steward 자신은 매이지 않는다 — 감사 대상이 아니다.)

## 절차

1. `python3 "$CLAUDE_SKILL_DIR/scripts/collect.py"` 실행 → `accepted` ADR 목록 + 두 하네스의 파일 인벤토리 + `pilots.md` 로드 결과 JSON.
2. **`pilots.md`의 파일럿 델타를 먼저 제외**한다(의도된 비정합 — 드리프트 아님).
3. 각 `accepted` ADR이 **어느 하네스를 구속하는지 먼저 매핑**한다 — 이것은 의미 판정이다(예: 문서 저작 규약 ADR은 ticket-engineer와 무관할 수 있다). 그다음 해당 하네스 파일을 읽어 **위반/누락/역행**을 판정한다:
   - **위반** — 하네스가 ADR에 반하는 지시를 담았다
   - **누락** — ADR이 요구하는 제약이 하네스에 없다
   - **역행** — 하네스가 옛(superseded) 정책을 아직 담고 있다
4. 교정은 `$OPS_WORKFLOW_ROOT/.claude/**` 또는 `$TICKET_ENGINEER_ROOT/**`를 **직접 편집**한다(쓰기 경계 안 — hook가 허용). 커밋 메시지에 **근거 ADR id**를 명시한다.

## 메타-프로세스 특별 규칙

`accepted` ADR이 "ADR을 어떻게 만드나" 자체(메타-프로세스)를 바꿨다면, **대응하는 ops-workflow 스크립트 변경도 같은 작업 단위**에 포함한다 — 정책과 그 집행 도구는 함께 움직인다. 안 그러면 도구와 정책이 어긋난다.

## 판정은 기계가 아니다

`collect.py`는 **무엇을 대조할지 모은다.** ADR이 하네스에 반영됐는지는 네가 **의미로 판정**한다. 애매하면 사용자에게 근거를 제시하고 묻는다.
