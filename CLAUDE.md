# ops-workflow-steward — 거버넌스 하네스

이 저장소는 **ops-workflow의 정책을 관리**하는 메타 시스템이다. 형제 저장소 `ops-workflow`(운영되는 시스템)를 **밖에서** 저작·감사·교정하며, 그 자신은 ops-workflow의 정책에 **매이지 않는다**.

---

## 0. 하나의 원칙 — 정책을 관리하는 자는 그 정책의 지배를 받지 않는다

이 하네스에는 ops-workflow **정책의 실질**(무엇을 결정했는가)이 **들어 있지 않다.** 그래야 그 정책을 사용자와 함께 재고·변경할 수 있다.

- ops-workflow의 `CLAUDE.md`·ADR은 여기서 **지시가 아니라 편집 대상 파일**이다.
- 그러므로 이 문서는 2-플레인·문서 3종·ADR 작성 규약 같은 **정책 내용을 재진술하지 않는다.** 필요하면 `$OPS_WORKFLOW_ROOT`의 ADR 코퍼스를 **읽는다.**
- 여기에 정책 실질 문장이 새어 들어오면 그것은 버그다 — steward의 자유가 깨진 것이다.

---

## 1. 대상 경로 — env var (`OPS_WORKFLOW_ROOT`)

- ops-workflow 로컬 경로는 **`OPS_WORKFLOW_ROOT`** env var로 주입한다. `.claude/settings.local.json`(**gitignored · PC별**)의 `env`에 둔다.
- 새 PC: `.claude/settings.local.example.json`을 `settings.local.json`으로 복사해 자기 경로를 채운다.
- 모든 스크립트·셸은 이 변수로 대상을 찾는다. **절대경로를 하드코딩하지 않는다.**
- ⚠ `env` 블록은 scope 간 **치환**(병합 아님)이다. `OPS_WORKFLOW_ROOT`가 유일 env면 `settings.local.json`에만 둔다.

---

## 2. 쓰기 경계 — 토픽 소유권

steward가 ops-workflow에 쓸 수 있는 곳은 둘뿐이다:

- `$OPS_WORKFLOW_ROOT/docs/ops-workflow/**` — 정책 문서(discussion·ADR)
- `$OPS_WORKFLOW_ROOT/.claude/**` — 하네스(전파·정합)

**그 외 `docs/<토픽>/**`은 docs-tickets의 것이다 — 쓰지 않는다.** 이 경계는 산문 규칙이 아니라 **PreToolUse hook**(`.claude/hooks/guard-write.py`)가 구조적으로 강제한다(§4).

---

## 3. 도구 — 정책 문서 저작은 ops-workflow의 스크립트로

steward는 ADR 저작 *메커니즘*을 새로 만들지 않는다. ops-workflow의 것을 **`$OPS_WORKFLOW_ROOT` 기준 경로**로 쓴다:

- ADR 번호·저작·accept·supersede·동결검사: `$OPS_WORKFLOW_ROOT/.claude/skills/adr/scripts/*.py`
- 티켓: `$OPS_WORKFLOW_ROOT/.claude/skills/ticket/scripts/*`
- 인덱스: `$OPS_WORKFLOW_ROOT/.claude/skills/docs-index/scripts/*`
- **`id`·`accepted_at`은 손으로 적지 않는다** — 스크립트가 채운다.

steward 자신의 스킬은 **감사 전용 둘뿐**이다: `coherence`(정합성) · `conformance`(하네스 정합).

---

## 4. 강제는 구조로 — 규율이 아니라

- 쓰기 경계: **PreToolUse hook**가 `$OPS_WORKFLOW_ROOT` 밖·타 토픽 Write/Edit를 거부한다.
- 동결·번호·게이트: ops-workflow의 스크립트가 거부한다(exit 1). steward는 **우회하지 않는다** — 왜 막혔는지 읽는다.
- "하지 마세요"를 최소화하고 **할 수 없게** 만든다.

---

## 5. 경계 — steward가 하지 않는 것

- ❌ `docs/<ops-workflow 외 토픽>/**` 쓰기 — docs-tickets 관할
- ❌ `accepted` ADR **본문** 수정 — 동결. 바꾸려면 **supersede**
- ❌ Issue close
- ❌ **자기 자신(이 저장소)의 프롬프트·스킬·CLAUDE.md 개정** — steward 하네스는 **사람이** 고친다. 자유의 원천은 사람이지 자기 자신이 아니다.

---

## 파일럿

`proposed`(미accept) 정책을 docs-tickets 하네스에 **시범 투입**할 때는 `pilots.md`에 기록한다. conformance 감사는 그 델타를 정합성 검사에서 제외한다.
