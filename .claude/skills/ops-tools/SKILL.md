---
name: ops-tools
description: ops-workflow의 저작 도구(ADR 번호·저작·accept·supersede·동결검사·티켓·인덱스)를 찾아 올바르게 실행한다. 정책 ADR을 쓰거나 accept/supersede하거나 티켓·인덱스를 다룰 때 반드시 먼저 본다.
---

# ops-tools — ops-workflow의 저작 도구를 찾아 쓴다

정책 문서 저작 *메커니즘*은 여기가 아니라 **ops-workflow**에 있다. steward는 adr·ticket·docs-index 스킬을 **자기 것으로 복제하지 않고**, ops-workflow의 스크립트를 **직접 구동**한다.

## ★ 반드시 지킬 것 — cwd

ops-workflow 스크립트는 대상 repo를 **CWD에서 `.git`을 위로 탐색**해 찾는다. steward는 자기 repo(별도 `.git`)가 cwd이므로, **절대경로로만 부르면 엉뚱한 repo(steward)를 대상으로 삼아 오작동**한다(예: `next-id`가 ADR-0001을 뱉는다).

→ **항상 `ops-run.py` 래퍼로 실행한다.** 래퍼가 cwd를 `$OPS_WORKFLOW_ROOT`로 바꾼다:

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/ops-run.py" <ops기준 상대경로> [args]
```

## 절차

**1. 도구 지도를 본다 (라이브 · 드리프트 없음):**
```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/list-ops-tools.py"
```
→ ops-workflow의 각 스킬·스크립트의 경로·목적·사용법을 그 자리에서 읽어 보여준다.

**2. 스크립트를 구동한다 (항상 래퍼로):**
```bash
# 예 — 번호 발급 → 경로 도출 → accept → supersede → 동결검사
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/ops-run.py" .claude/skills/adr/scripts/next-id.py
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/ops-run.py" .claude/skills/adr/scripts/accept.py ADR-0009
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/ops-run.py" .claude/skills/adr/scripts/supersede.py --old ADR-0003 --by ADR-0009
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/ops-tools/scripts/ops-run.py" .claude/skills/adr/scripts/freeze-check.py docs/ops-workflow/adr/adr-0003-....md
```

**3. 판단 맥락이 필요하면** `$OPS_WORKFLOW_ROOT/.claude/skills/adr/SKILL.md`를 읽는다.

## 손대지 않는 것 (기계가 한다)

- `id`·`accepted_at`은 **손으로 적지 않는다** — `next-id.py`·`accept.py`가 채운다.
- `accepted` 문서 본문·경로는 **동결**이다 — 고치기 전 `freeze-check.py`. 바꾸려면 `supersede.py`.
- `docs/` 커밋은 **사람이 승인**한다.

## 판단 규약은 steward의 법이 아니다

`adr/SKILL.md`의 판단 절(임계선·입도·why-only·자족성)은 **현행 정책**이다. 기본으로 따르되, **정책 관리자로서 사용자와 함께 재고**할 수 있다 — 프롬프트-법이 아니라 편집 대상이다(`CLAUDE.md` §0).

## conformance 주의

steward가 ops-workflow 스크립트나 SKILL.md를 (역할 3으로) 바꾸면, **docstring과 SKILL.md도 함께 갱신**한다 — `list-ops-tools.py`와 미래의 독자가 그것을 읽는다. 정책과 그 집행 도구·문서는 함께 움직인다.
