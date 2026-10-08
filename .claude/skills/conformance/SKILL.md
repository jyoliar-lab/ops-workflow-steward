---
name: conformance
description: 공표된 정책 ADR과 피관리 하네스(ops-workflow 역할 하네스·ticket-engineer)의 정합성 검토·교정. "하네스가 정책과 어긋났나", "정책을 하네스에 반영", "정합성 전파"일 때.
---

# conformance — 하네스 정합·전파

**공표된 정책 ADR**이 피관리 하네스에 반영돼 있는지 확인하고, 어긋나면 **교정**한다. 기준선은 `accepted`가 아니다 — 정책 ADR은 `proposed`가 현행 규범이다(ADR-0032). 공표란 origin/main에 있다는 뜻이다. 피관리 하네스는 두 저장소에 있다:

- **ops-workflow** — 규약 `$OPS_WORKFLOW_ROOT/CLAUDE.md` · 공통 `.claude/**` · 역할별 `harness/<역할>/`(design-partner · adr-judge — 각각 `CLAUDE.md`와 `.claude/skills/`)
- **ticket-engineer** — `$TICKET_ENGINEER_ROOT`의 `CLAUDE.md`·`.claude/**`

둘 다 정책에 "매여" 있으므로, 그 매임의 내용을 최신 정책으로 유지하는 것이 목적. (steward 자신은 매이지 않는다 — 감사 대상이 아니다.)

## 절차

1. `python3 "${CLAUDE_SKILL_DIR}/scripts/collect.py"` 실행 → 공표된 정책 ADR 목록(origin/main 기준, `proposed`·`accepted`) + 공표 전 로컬 ADR + 두 하네스의 파일 인벤토리 + `pilots.md` 경로 JSON.
2. `pilots.md`(롤백 원장)를 읽어 **어느 ADR의 델타가 어디에 들어갔는지** 안다 — 대조의 출발점이지 제외 목록이 아니다.
3. 각 공표 ADR이 **어느 하네스를 구속하는지 먼저 매핑**한다 — 이것은 의미 판정이다(예: 문서 저작 규약 ADR은 ticket-engineer와 무관할 수 있다). 그다음 해당 하네스 파일을 읽어 **위반/누락/역행**을 판정한다:
   - **위반** — 하네스가 ADR에 반하는 지시를 담았다
   - **누락** — ADR이 요구하는 제약이 하네스에 없다
   - **역행** — 하네스가 옛 정책을 아직 담고 있다 — `superseded`된 것, 또는 `proposed` 본문이 고쳐졌는데 하네스는 옛 본문을 따르는 것
4. 교정은 `$OPS_WORKFLOW_ROOT/.claude/**` 또는 `$TICKET_ENGINEER_ROOT/**`를 **직접 편집**한다(쓰기 경계 안 — CLAUDE.md §2). 커밋 메시지에 **근거 ADR id**를 명시한다.

## 커밋 단위 — 정책과 그 반영은 함께 움직인다

**ADR의 생성·수정이 하네스 델타를 낳으면, 그 델타는 ADR과 한 작업 단위로 커밋한다** — adr-judge 심사가 돌아온 뒤에. 묶음 규칙(같은 repo = 같은 커밋 · ticket-engineer = ADR id 명시한 동반 커밋 · `pilots.md` 행 포함)과 승인 절차는 **steward `CLAUDE.md` §3 "커밋 단위"** 가 정본이다.

그 한 사례가 메타-프로세스다: 정책 ADR이 "ADR을 어떻게 만드나" 자체를 바꿨다면, **대응하는 ops-workflow 스크립트 변경도 같은 작업 단위**에 포함한다 — 안 그러면 도구와 정책이 어긋난다.

## 판정은 기계가 아니다

`collect.py`는 **무엇을 대조할지 모은다.** ADR이 하네스에 반영됐는지는 네가 **의미로 판정**한다. 애매하면 사용자에게 근거를 제시하고 묻는다.
