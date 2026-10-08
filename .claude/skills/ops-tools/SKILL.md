---
name: ops-tools
description: ops-workflow의 저작 도구를 찾아 올바르게 구동한다 — ADR 저작·accept·supersede·동결검사(adr), 문서 변경 후 인덱스 재생성(build-index.py), 정책 티켓 발행·연결(ticket). 정책 문서를 쓰거나 고치거나, 인덱스를 갱신하거나, 정책 티켓을 다룰 때 먼저 본다.
---

# ops-tools — ops-workflow의 저작 도구를 찾아 쓴다

정책 문서 저작 *메커니즘*은 여기가 아니라 **ops-workflow**에 있다. steward는 그 스킬들을 **자기 것으로 복제하지 않고** 직접 구동한다. 구동 대상은 ops-workflow 안의 네 자리에 있다(경로는 ops-workflow 루트 기준):

- **`adr`**(공통, `.claude/skills/adr/`) — 번호·경로·subjects 어휘·동결검사
- **`adr-accept`**(`harness/adr-judge/.claude/skills/adr-accept/`) — accept·unaccept·supersede
- **`ticket`**(`harness/design-partner/.claude/skills/ticket/`) — 정책 관련 GitHub Issue 발행·하위 연결·사후 기입
- **`build-index.py`**(`.claude/scripts/`, 스킬 아님) — 문서를 추가·변경·accept·supersede한 뒤 `_index/` 재생성. ops-workflow 안에서는 PostToolUse hook가 자동으로 돌리지만 **steward 세션에는 그 hook가 없다** — 직접 돌린다.

## ★ 반드시 지킬 것 — cwd

ops-workflow 스크립트는 대상 repo를 **CWD에서 `.git`을 위로 탐색**해 찾는다. steward는 자기 repo(별도 `.git`)가 cwd이므로, **절대경로로만 부르면 엉뚱한 repo(steward)를 대상으로 삼아 오작동**한다(예: `next-id`가 ADR-0001을 뱉는다).

→ **cwd를 `$OPS_WORKFLOW_ROOT`로 두고 실행한다.** 둘은 동치다:

```bash
python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/ops-tools/scripts/ops-run.py" <ops기준 상대경로> [args]
cd "$OPS_WORKFLOW_ROOT" && python3 <ops기준 상대경로> [args]
```

## 절차

**1. 도구 지도를 본다 (라이브 · 드리프트 없음):**
```bash
python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/ops-tools/scripts/list-ops-tools.py"
```
→ 공통 스킬·역할 하네스 스킬·`.claude/scripts/`의 스크립트 경로·목적·사용법을 그 자리에서 읽어 보여준다.

**2. 스크립트를 구동한다 (항상 `ops-run.py` 래퍼로).** 아래는 대표 예이며, 정확한 인자는 1단계 지도 또는 각 SKILL.md를 본다:
```bash
WRAP="${CLAUDE_PROJECT_DIR}/.claude/skills/ops-tools/scripts/ops-run.py"

# adr — 저작 (공통)
python3 "$WRAP" .claude/skills/adr/scripts/list-subjects.py
python3 "$WRAP" .claude/skills/adr/scripts/next-id.py
python3 "$WRAP" .claude/skills/adr/scripts/doc-path.py --topic ops-workflow --id ADR-0009 --slug <slug>
python3 "$WRAP" .claude/skills/adr/scripts/freeze-check.py <path>

# adr-accept — 전이 (adr-judge 하네스)
python3 "$WRAP" harness/adr-judge/.claude/skills/adr-accept/scripts/accept.py ADR-0009
python3 "$WRAP" harness/adr-judge/.claude/skills/adr-accept/scripts/supersede.py --old ADR-0003 --by ADR-0009

# ticket — 정책 관련 Issue (design-partner 하네스, 필요 시)
python3 "$WRAP" harness/design-partner/.claude/skills/ticket/scripts/create.py --type task --title "..." --body-file <path> [--adr ADR-NNNN]
python3 "$WRAP" harness/design-partner/.claude/skills/ticket/scripts/link-sub.py --parent <N> --child <M>

# 인덱스 — 문서를 바꾼 뒤 반드시 (steward 세션에는 자동 재생성 hook가 없다)
python3 "$WRAP" .claude/scripts/build-index.py
```

**3. ★ 문서를 추가·변경·accept·supersede했으면 인덱스를 재생성한다** — `build-index.py`. `_index/`는 **생성물**이라 안 돌리면 낡는다. 저작·전이의 마지막 단계로 잊지 않는다.

**4. ★ 커밋 단위** — ADR 생성·수정에 하네스 델타가 따르면 **함께 커밋**한다. 묶음 규칙과 승인 절차는 **`CLAUDE.md` §3 "커밋 단위"** 가 정본이다 — 사용자 승인 없이 커밋하지 않는다.

**5. 판단 맥락이 필요하면** 해당 스킬의 SKILL.md(`$OPS_WORKFLOW_ROOT/.claude/skills/<skill>/SKILL.md`)를 읽는다.

## 손대지 않는 것 (기계가 한다)

- `id`·`accepted_at`은 **손으로 적지 않는다** — `next-id.py`·`accept.py`가 채운다.
- `accepted` 문서 본문·경로는 **동결**이다 — 고치기 전 `freeze-check.py`. 바꾸려면 `supersede.py`.
- `_index/`는 손으로 고치지 않는다 — **`build-index.py`의 생성물**이다.
- 컨테이너 티켓(epic·feature)은 **accepted ADR을 전제**한다 — `ticket`의 게이트가 막는다. 우회하지 않는다.
- `docs/` 커밋은 **사람이 승인**한다.

## 판단 규약은 steward의 법이 아니다

각 스킬 SKILL.md의 판단 절(특히 `adr`의 임계선·입도·why-only·자족성)은 **현행 정책**이다. 기본으로 따르되, **정책 관리자로서 사용자와 함께 재고**할 수 있다 — 프롬프트-법이 아니라 편집 대상이다(`CLAUDE.md` §0).

## conformance 주의

steward가 ops-workflow 스크립트나 SKILL.md를 (역할 3으로) 바꾸면, **docstring과 SKILL.md도 함께 갱신**한다 — `list-ops-tools.py`와 미래의 독자가 그것을 읽는다. 정책과 그 집행 도구·문서는 함께 움직인다.
